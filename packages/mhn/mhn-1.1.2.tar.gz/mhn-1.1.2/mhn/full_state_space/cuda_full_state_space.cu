// by Stefan Vocht, Linda Hu
// this file contains CUDA functions to compute
// the gradients for training a MHN on full state-space

#include "cuda_runtime.h"
#include "device_launch_parameters.h"

#include <cuda.h>
#include <cuda_runtime_api.h>

#include <stdio.h>
#include <math.h>

#include "cuda_inverse_by_substitution.cuh"

// on Windows we need to add a prefix in front of the function we want to use in other code
// on Linux this is not needed, so we define DLL_PREFIX depending on which os this code is compiled on
#ifdef _WIN32
#define DLL_PREFIX __declspec(dllexport)
#else
#define DLL_PREFIX
#endif

// minimum number of thread blocks used by CUDA
#define MIN_BLOCK_NUM 32

/**
 * we determine the number of blocks and threads used in the CUDA kernels for the current data point with this function
 *
 * @param[out] block_num number of blocks that should be used for the CUDA kernels
 * @param[out] thread_num number of threads that should be used for the CUDA kernels
 * @param[in] n size of the MHN
 */
static void determine_block_thread_num(int &block_num, int &thread_num, const int n)
{

    // block_num and thread_num have to be powers of two, else cuda_kronvec will not work
    // maximum 256 blocks with 1024 threads
    if (n >= 17)
    {
        block_num = 256;
        thread_num = 512;
    }
    // define a minimum number of blocks and threads per block
    else if (n < 12)
    {
        block_num = MIN_BLOCK_NUM;
        thread_num = 64;
    }
    else
    {
        block_num = 1 << (n / 2);
        thread_num = 1 << (n / 2 + (n & 1));
    }
}

/**
 * this function is the cuda implementation of the kronvec function for full state-space
 *
 * IMPORTANT: the result is added to the entries of pout! This makes the q_vec function more efficient.
 * If you need the result without adding, initialize pout with zeros.
 *
 * @param[in] ptheta array containing the values of theta
 * @param[in] i vector is multiplied with the ith kronecker product (ith summand in eq. 9 of the original paper)
 * @param[in] px vector that is multiplied with the kronecker product
 * @param[in] diag if false, the diagonal of the kronecker product is set to zero
 * @param[in] transp if true, the kronecker product is transposed
 * @param[in] n total number of genes considered by the MHN, also column and row size of theta
 * @param[out] pout vector which will contain the result of this multiplication
 */
__global__ void cuda_kronvec(const double *__restrict__ ptheta, const int i, const double *__restrict__ px, const bool diag, const bool transp, const int n, double *__restrict__ pout)
{
    const int stride = blockDim.x * gridDim.x;
    const int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    // in the following 1 << i is equivalent to 2^i, x >> i is equivalent to x // 2^i, x & ((1<<i)-1) to x % 2^i
    const int nx = 1 << n;

    extern __shared__ double theta_i[];

    // load the ith row of theta into shared memory for more efficient access
    for (int j = threadIdx.x; j < n; j += blockDim.x)
    {
        theta_i[j] = ptheta[i * n + j];
    }

    __syncthreads();

    // patch_size is important for later for the case i == j in the shuffle algorithm
    // as we do not actually shuffle the data in px in this implementation (only implicitly), we have to keep track of some indices
    // and which entries have to be computed together in the case i == j. Those two indices are (x_index) and (x_index + patch_size)
    // ("patch_size", as over all, the entries that have to be computed together occur in patches of size 2**(count_before_i))
    const int patch_size = 1 << i;
    int x_index = ((cuda_index >> i) << (i + 1)) + (cuda_index & (patch_size - 1));

    // for each iteration of this while loop, we compute the output values for indices (x_index) and (x_index + patch_size)
    // and add the result to pout
    while (x_index + patch_size < nx)
    {
        // for each entry the theta_ij that have to be multiplied to give us the correct result are given
        // by the bit representation of its index:
        // if the kth bit of the index is set to 1 we have to use theta_ik to compute the output
        // as patch_size is a power of two, (x_index) and (x_index + patch_size) only differ in a single bit,
        // namely the ith one
        double theta_product = 1.;

        int x_index_copy = x_index;
        double theta;

        for (int j = 0; j < n; j++)
        {
            theta = theta_i[j];
            if (i == j)
            {
                // if i == j then that theta is always part of theta_product
                theta_product *= theta;
            }
            else
            {
                // if the current first bit of x_index_copy is set to 1, multiply with theta
                // else multiply with one
                // here the if condition is implicitly in the computation to avoid branching of the threads
                theta_product *= 1. + (x_index_copy & 1) * (theta - 1.);
            }
            // shift the bits by one for the next iteration
            x_index_copy >>= 1;
        }

        // we now have to make computations involving the entries (x_index) and (x_index + patch_size)
        // this is the part for which it was important to choose the correct patch_size and why we needed to compute two entries at once
        // the following computations follow from the part of the shuffle algorithm where we multiply the 2x2 matrix containing theta_ii with px
        if (!transp)
        {
            double output = px[x_index] * theta_product;
            pout[x_index + patch_size] += output;
            if (diag)
            {
                pout[x_index] -= output;
            }
        }
        else
        {
            if (diag)
            {
                // this case never occurs during gradient computation, its just here for the sake of completeness
                pout[x_index] += (px[x_index + patch_size] - px[x_index]) * theta_product;
            }
            else
            {
                pout[x_index] += px[x_index + patch_size] * theta_product;
            }
        }

        // if patch_size is bigger than stride, we have to do corrections to the indices
        if (stride < patch_size)
        {
            // check if the current index is inside an odd patch, if so, jump to the next one
            x_index += stride;
            x_index += ((x_index >> i) & 1) * patch_size;
        }
        else
        {
            x_index += 2 * stride;
        }
    }
}

/**
 * computes y = Q(ptheta) * x, result is saved in yout
 *
 * important: ptheta, x and yout must be allocated using cudaMalloc()!
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] x vector that should be multiplied with Q(ptheta)
 * @param[out] yout array in which the result is stored
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[in] diag if false, the diag of Q is set to zero during multiplication
 * @param[in] transp if true, multiplication is done with the transposed Q
 */
static void cuda_q_vec(const double *__restrict__ ptheta, const double *__restrict__ x, double *__restrict__ yout, const int n, const bool diag, const bool transp)
{

    const int nx = 1 << n;
    cudaMemset(yout, 0, nx * sizeof(double));

    int block_num, thread_num;

    determine_block_thread_num(block_num, thread_num, n);

    for (int i = 0; i < n; i++)
    {
        cuda_kronvec<<<block_num, thread_num, n * sizeof(double)>>>(ptheta, i, x, diag, transp, n, yout);
    }
}

/**
 * computes the ith subdiagonal of Q and subtracts(!) it from dg
 * we subtract it, because in jacobi() we need 1 - dg, so dg is initialized with 1 and we subtract the subdiags
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] i this function computes the ith subdiagonal
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[in, out] dg the subdiagonal is subtracted from the values in this array
 */
static __global__ void cuda_subdiag(const double *__restrict__ ptheta, const int i, const int n, double *__restrict__ dg)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    // in the following 1 << i is equivalent to 2^i, x >> i is equivalent to x // 2^i, x & ((1<<i)-1) to x % 2^i
    const int nx = 1 << n;

    // store the ith row of theta in shared memory for more efficient access
    extern __shared__ double theta_i[];

    for (int j = threadIdx.x; j < n; j += blockDim.x)
    {
        theta_i[j] = ptheta[i * n + j];
    }
    __syncthreads();

    for (int k = cuda_index; k < nx; k += stride)
    {

        double dg_entry = 1;

        int position_condition = k;
        for (int j = 0; j < n; j++)
        {
            double theta = theta_i[j];
            // depending on the index different thetas have to be multiplied to the subdiag entry
            if (i == j)
            {
                dg_entry *= -(1 - (position_condition & 1)) * theta;
            }
            else
            {
                dg_entry *= 1 + (position_condition & 1) * (theta - 1);
            }
            position_condition >>= 1;
        }
        // subtract the subdiagonal from the diagonal entries
        dg[k] -= dg_entry;
    }
}

/**
 * subtracts the diag of Q from the given dg array, result can be found in dg
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[in, out] dg the subdiagonals are subtracted from the values in this array
 * @param[in] block_num number of blocks used for the CUDA kernels
 * @param[in] thread_num  number of threads used for the CUDA kernels
 */
static void cuda_subtract_q_diag(const double *__restrict__ ptheta, const int n, double *__restrict__ dg, int block_num, int thread_num)
{
    for (int i = 0; i < n; i++)
    {
        cuda_subdiag<<<block_num, thread_num, n * sizeof(double)>>>(ptheta, i, n, dg);
    }
}

static __global__ void fill_array(double *arr, double x, const int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        arr[k] = x;
    }
}

static __global__ void add_arrays(const double *arr1, double *arr_inout, const int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        arr_inout[k] += arr1[k];
    }
}

static __global__ void divide_arrays_elementwise(const double *arr1, const double *arr2, double *out, const int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        out[k] = arr1[k] / arr2[k];
    }
}

static __global__ void multiply_arrays_elementwise(const double *arr1, double *arr_inout, const int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        arr_inout[k] *= arr1[k];
    }
}

/**
 * this function computes the diagonal of [I-Q] for the jacobi function
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[out] dg this array will contain the diagonal of [I-Q] after calling this function, has size must have size 2^mutation_num
 */
static void compute_jacobi_diagonal(const double *__restrict__ ptheta, const int n, double *__restrict__ dg)
{
    const int nx = 1 << n;

    int block_num, thread_num;
    determine_block_thread_num(block_num, thread_num, n);

    // initialize the diagonal entries
    fill_array<<<block_num, thread_num>>>(dg, 1, nx);
    cuda_subtract_q_diag(ptheta, n, dg, block_num, thread_num);
}

/**
 * this functions multiplies [I-Q]^(-1) with b
 * all arrays given to this function must be allocated using cudaMalloc()
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] b array that is multiplied with [I-Q]^(-1)
 * @param[in] transp if true, b is multiplied with the transposed [I-Q]^(-1)
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[out] xout the results of this function are stored in this array
 * @param[in, out] tmp this array is used to store temporary data, has to have size 2^n
 * @param[in] dg this array contains the diagonal of [I-Q]
 */
static void cuda_jacobi(const double *__restrict__ ptheta, const double *__restrict__ b, const bool transp, const int n, double *__restrict__ xout, double *__restrict__ tmp, double *__restrict__ dg)
{

    const int nx = 1 << n;

    int block_num, thread_num;
    determine_block_thread_num(block_num, thread_num, n);

    // initialize the entries of xout with 1/nx
    fill_array<<<block_num, thread_num>>>(xout, 1. / (1. * nx), nx);

    // compute the product of [I-Q]^(-1) with b
    for (int z = 0; z < n + 1; z++)
    {
        cuda_q_vec(ptheta, xout, tmp, n, false, transp);
        add_arrays<<<block_num, thread_num>>>(b, tmp, nx);
        divide_arrays_elementwise<<<block_num, thread_num>>>(tmp, dg, xout, nx);
    }
}

/**
 * this functions shuffles the entries of old_vec into the entries of to_shuffle_vec
 *
 * @param[in] old_vec array that should be shuffled
 * @param[out] to_shuffle_vec array in which the shuffled vector is stored
 * @param[in] nx size of both vectors
 */
static __global__ void shuffle(const double *__restrict__ old_vec, double *__restrict__ to_shuffle_vec, const int nx)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < nx; k += stride)
    {
        int greater_than_nx = (k >= nx / 2);
        to_shuffle_vec[k] = old_vec[2 * (k - greater_than_nx * nx / 2) + greater_than_nx];
    }
}

/**
 * this functions shuffles the entries of old_vec into the entries of to_shuffle_vec in reverse
 *
 * @param[in] old_vec array that should be shuffled
 * @param[out] to_shuffle_vec array in which the shuffled vector is stored
 * @param[in] nx size of both vectors
 */
static __global__ void rev_shuffle(const double *__restrict__ old_vec, double *__restrict__ to_shuffle_vec, const int nx)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < nx; k += stride)
    {
        int greater_than_nx = (k >= nx / 2);
        to_shuffle_vec[2 * (k - greater_than_nx * nx / 2) + greater_than_nx] = old_vec[k];
    }
}

/**
 * inspired by https://developer.download.nvidia.com/assets/cuda/files/reduction.pdf
 * computes the sum of all entries in a given array
 */
static __global__ void sum_over_array(const double *__restrict__ arr, double *__restrict__ result, int size)
{

    extern __shared__ double sdata[];

    unsigned int tid = threadIdx.x;
    unsigned int stride = blockDim.x * gridDim.x;
    unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;

    double partial_sum = 0;

    for (unsigned int s = i; s < size; s += stride)
    {
        partial_sum += arr[s];
    }

    sdata[tid] = partial_sum;
    __syncthreads();

    for (unsigned int s = blockDim.x / 2; s > 0; s >>= 1)
    {
        if (tid < s)
        {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0)
        result[blockIdx.x] = sdata[0];
}

static __global__ void print_vec(double *vec, int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        printf("%g, ", vec[k]);
    }
    if (cuda_index == 0)
    {
        printf("\n\n");
    }
}

static __global__ void log_array(const double *__restrict__ input, double *__restrict__ output, int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int k = cuda_index; k < size; k += stride)
    {
        output[k] = log(input[k]);
    }
}

/**
 * computes the marginal log-likelihood score given the relative frequency of observed tumours and the probability distribution yielded by the MHN
 *
 * @param[in] pD relative frequency of observed tumours in the data
 * @param[in] pth probability distribution yielded by the MHN
 * @param[in] n number of genes considered by the MHN
 * @param[out] score_out the marginal log-likelihood score is stored at this address
 * @param[in, out] tmp1 allocated memory of size 2^n needed by this function to operate
 * @param[in, out] tmp2 allocated memory of size >=1024 needed by this function to operate
 */
static void compute_score(const double *__restrict__ pD, const double *__restrict__ pth, int n, double *__restrict__ score_out, double *__restrict__ tmp1, double *__restrict__ tmp2)
{
    int nx = 1 << n;
    int block_num, thread_num;
    determine_block_thread_num(block_num, thread_num, n);

    log_array<<<block_num, thread_num>>>(pth, tmp1, nx);
    multiply_arrays_elementwise<<<block_num, thread_num>>>(pD, tmp1, nx);
    sum_over_array<<<block_num, thread_num, thread_num * sizeof(double)>>>(tmp1, tmp2, nx);
    sum_over_array<<<1, block_num, block_num * sizeof(double)>>>(tmp2, score_out, block_num);
}

/**
 * compute the gradient for a given relative frequency of observed tumours in the data
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[out] grad array that will contain the gradient at the end, size n*n
 * @param[in] pD relative frequency of observed tumours in the data, size 2^n
 * @param[in] pth memory buffer needed for this function, size 2^n
 * @param[in] q memory buffer needed for this function, size 2^n
 * @param[in] tmp1 memory buffer needed for this function, size 2^n
 * @param[in] tmp2 memory buffer needed for this function, size 2^n
 * @param[out] score the marginal log-likelihood score of the MHN will be stored here
 */
static void cuda_gradient_and_score_computation(const double *__restrict__ ptheta, const int n, double *__restrict__ grad, double *__restrict__ pD, double *__restrict__ pth, double *__restrict__ q, double *__restrict__ tmp1, double *__restrict__ tmp2, double *__restrict__ score)
{

    const int nx = 1 << n;
    int block_num, thread_num;
    determine_block_thread_num(block_num, thread_num, n);

    // alias tmp1 and tmp2 for the first part of this function for better readability
    double *p0 = tmp1;
    double *dg = tmp2;

    // set all entries of p0 to zero, set the first entry to one
    cudaMemset(pth, 0, nx * sizeof(double));
    fill_array<<<1, 1>>>(pth, 1., 1);

    // compute the diagonal for the jacobi calls
    compute_jacobi_diagonal(ptheta, n, dg);

    // q is here only used as temporary memory, because the memory is not needed yet for anything else
    // cuda_jacobi(ptheta, p0, false, n, pth, q, dg);
    // cudaMemcpy(pth, p0, nx * sizeof(double), cudaMemcpyDeviceToDevice);
    _compute_inverse(ptheta, n, dg, pth, false);

    divide_arrays_elementwise<<<block_num, thread_num>>>(pD, pth, pD, nx);

    // here p0 is used as temporary memory, because we do not need its contents any longer
    // cuda_jacobi(ptheta, pD, true, n, q, p0, dg);
    cudaMemcpy(q, pD, nx * sizeof(double), cudaMemcpyDeviceToDevice);
    _compute_inverse(ptheta, n, dg, q, true);

    double *old_vec, *shuffled_vec, *swap_vec;

    multiply_arrays_elementwise<<<block_num, thread_num>>>(pth, pD, nx);
    compute_score(pD, pth, n, score, tmp1, tmp2);

    for (int i = 0; i < n; i++)
    {
        cudaMemset(tmp1, 0, nx * sizeof(double));

        cuda_kronvec<<<block_num, thread_num, n * sizeof(double)>>>(ptheta, i, pth, true, false, n, tmp1);

        // tmp1 contains the result of the call to cuda_restricted_kronvec above
        multiply_arrays_elementwise<<<block_num, thread_num>>>(q, tmp1, nx);

        old_vec = tmp1;
        shuffled_vec = tmp2;
        double *grad_i = grad + i * n;

        // use the shuffle trick for a more efficient computation of the gradient
        for (int j = 0; j < n; j++)
        {
            // confusion warning: the pD here has nothing to do with the former pD above
            // in this section pD is used again, because we need an allocated array and pD isnt needed anymore so we can just use that as memory
            shuffle<<<block_num, thread_num>>>(old_vec, shuffled_vec, nx);
            if (i == j)
            {
                sum_over_array<<<block_num, thread_num, thread_num * sizeof(double)>>>(shuffled_vec, pD, nx);
                sum_over_array<<<1, block_num, block_num * sizeof(double)>>>(pD, grad_i + i, block_num);
            }
            else
            {
                sum_over_array<<<block_num, thread_num, thread_num * sizeof(double)>>>(shuffled_vec + nx / 2, pD, nx / 2);
                sum_over_array<<<1, block_num, block_num * sizeof(double)>>>(pD, grad_i + j, block_num);
            }

            swap_vec = old_vec;
            old_vec = shuffled_vec;
            shuffled_vec = swap_vec;
        }
    }
}

static __global__ void set_uneven_1(double *arr, int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int i = cuda_index; i < size / 2; i += stride)
    {
        arr[2 * i + 1] = 1;
    }
}

/**
 * compute the Fisher Information Matrix for a given relative frequency of observed tumours in the data
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[out] fim array that will contain the Fisher Information Matrix at the end, size n^2*n^2
 * @param[in] pth memory buffer needed for this function, size 2^n
 * @param[in] zero_mask memory buffer needed for this function, size 2^n
 * @param[in] dg memory buffer needed for this function, size 2^n
 * @param[in] dQ_st memory buffer needed for this function, size 2^n
 * @param[in] dQ_ij memory buffer needed for this function, size 2^n
 * @param[in] masked_dQ_st memory buffer needed for this function, size 2^n
 * @param[in] q_st memory buffer needed for this function, size 2^n
 * @param[in] temp memory buffer needed for this function, size 2^n
 * @param[in] temp_score memory buffer needed for this function, size 1
 */
static void fisher_upper(
    const double *__restrict__ ptheta,
    const int n,
    double *__restrict__ fim,
    double *__restrict__ pth,
    double *__restrict__ zero_mask,
    double *__restrict__ dg,
    double *__restrict__ dQ_st,
    double *__restrict__ dQ_ij,
    double *__restrict__ masked_dQ_st,
    double *__restrict__ q_st,
    double *__restrict__ temp,
    double *__restrict__ temp_score)
{

    const int nx = 1 << n;
    const int nx_half = nx / 2;
    const int n_sq = n * n;

    int block_num, thread_num;
    determine_block_thread_num(block_num, thread_num, n);

    double *shuffled_vec = temp;
    double *swap_vec;

    double temp_score_host;

    int ind_x;
    int ind_y;

    // set all entries of p0 to zero, set the first entry to one
    cudaMemset(pth, 0, nx * sizeof(double));
    fill_array<<<1, 1>>>(pth, 1., 1);

    // compute the diagonal for the jacobi calls
    compute_jacobi_diagonal(ptheta, n, dg);

    _compute_inverse(ptheta, n, dg, pth, false);

    ind_x = -1;

    for (int s = 0; s < n; s++)
    {

        // set all elements of dQ to zero
        cudaMemset(dQ_st, 0, nx * sizeof(double));

        cuda_kronvec<<<block_num, thread_num, n * sizeof(double)>>>(ptheta, s, pth, true, false, n, dQ_st);

        // set up the zero mask
        cudaMemset(zero_mask, 0, nx * sizeof(double));
        set_uneven_1<<<block_num, thread_num>>>(zero_mask, nx);

        for (int t = 0; t < n; t++)
        {

            // copy dQ_st to masked_dQ_st
            cudaMemcpy(masked_dQ_st, dQ_st, nx * sizeof(double), cudaMemcpyDeviceToDevice);

            if (s != t)
            {
                multiply_arrays_elementwise<<<block_num, thread_num>>>(zero_mask, masked_dQ_st, nx);
            }

            // shuffle zero mask
            rev_shuffle<<<block_num, thread_num>>>(zero_mask, shuffled_vec, nx);

            swap_vec = shuffled_vec;
            shuffled_vec = zero_mask;
            zero_mask = swap_vec;

            cudaMemcpy(q_st, masked_dQ_st, nx * sizeof(double), cudaMemcpyDeviceToDevice);
            _compute_inverse(ptheta, n, dg, q_st, false);

            divide_arrays_elementwise<<<block_num, thread_num>>>(q_st, pth, shuffled_vec, nx);
            swap_vec = q_st;
            q_st = shuffled_vec;
            shuffled_vec = swap_vec;

            _compute_inverse(ptheta, n, dg, q_st, true);

            ind_x += 1;
            ind_y = s * n;

            for (int i = s; i < n; i++)
            {

                // set all elements of dQ to zero
                cudaMemset(dQ_ij, 0, nx * sizeof(double));
                cuda_kronvec<<<block_num, thread_num, n * sizeof(double)>>>(ptheta, i, pth, true, false, n, dQ_ij);

                multiply_arrays_elementwise<<<block_num, thread_num>>>(q_st, dQ_ij, nx);

                for (int j = 0; j < n; j++)
                {
                    
                    shuffle<<<block_num, thread_num>>>(dQ_ij, shuffled_vec, nx);
                    
                    swap_vec = dQ_ij;
                    dQ_ij = shuffled_vec;
                    shuffled_vec = swap_vec;

                    if (ind_y >= ind_x)
                    {

                        if (i == j)
                        {
                            sum_over_array<<<block_num, thread_num, thread_num * sizeof(double)>>>(dQ_ij, shuffled_vec, nx);
                            sum_over_array<<<1, block_num, block_num * sizeof(double)>>>(shuffled_vec, fim + ind_x * n_sq + ind_y, block_num);
                        }
                        
                        else
                        {
                            sum_over_array<<<block_num, thread_num, thread_num * sizeof(double)>>>(dQ_ij + nx_half, shuffled_vec, nx_half);
                            sum_over_array<<<1, block_num, block_num * sizeof(double)>>>(shuffled_vec, fim + ind_x * n_sq + ind_y, block_num);
                        }                           
                    }

                    ind_y += 1;

                }
            }
        }
    }
}

static __global__ void array_exp(double *arr, int size)
{
    int stride = blockDim.x * gridDim.x;
    int cuda_index = blockIdx.x * blockDim.x + threadIdx.x;

    for (int i = cuda_index; i < size; i += stride)
    {
        arr[i] = exp(arr[i]);
    }
}

/**
 * this function computes the gradient and score for the current MHN for a given observed frequency of tumors in data using CUDA
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[in] pD observed frequency of tumors in data
 * @param[out] grad_out array of size n*n in which the gradient will be stored
 * @param[out] score_out the marginal log-likelihood score is stored at this position
 *
 * @return CUDA error code converted to integer for better interoperability with Cython
 */
extern "C" int DLL_PREFIX cuda_full_state_space_gradient_score(double *ptheta, int n, double *pD, double *grad_out, double *score_out)
{

    int nx = 1 << n;
    // the arrays have to be at least of size MIN_BLOCK_NUM, else there will be errors when summing over arrays
    if (nx < MIN_BLOCK_NUM)
    {
        nx = MIN_BLOCK_NUM;
    }

    double *cuda_grad_out;
    double *cuda_pD, *pth, *q, *tmp1, *tmp2;
    double *cuda_ptheta;
    double *cuda_score;

    // allocate memory on the GPU
    // we allocate all at once so that we can easily check for allocation errors
    // if we did each allocation as a separate cudaMalloc, we would have to check for errors after each single call
    double *d_memory;
    cudaMalloc(&d_memory,
               n * n * sizeof(double) +     // cuda_grad_out
                   nx * sizeof(double) +    // p0_pD
                   nx * sizeof(double) +    // pth
                   nx * sizeof(double) +    // q
                   nx * sizeof(double) +    // tmp1
                   nx * sizeof(double) +    // tmp2
                   n * n * sizeof(double) + // cuda_ptheta
                   1 * sizeof(double)       // cuda_score
    );

    // check for errors
    // errors could occur if CUDA is not installed correctly or if the user tries to allocate too much memory
    if (cudaPeekAtLastError() != cudaSuccess)
    {
        // cast cudaError_t to int, not the best style, but simplest method to get it work in Cython
        return (int)cudaPeekAtLastError();
    }

    cuda_grad_out = d_memory;
    cuda_pD = d_memory + n * n;
    pth = d_memory + n * n + nx;
    q = d_memory + n * n + 2 * nx;
    tmp1 = d_memory + n * n + 3 * nx;
    tmp2 = d_memory + n * n + 4 * nx;
    cuda_ptheta = d_memory + n * n + 5 * nx;
    cuda_score = d_memory + 2 * n * n + 5 * nx;

    // copy theta and pD to the GPU
    cudaMemcpy(cuda_ptheta, ptheta, n * n * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy(cuda_pD, pD, nx * sizeof(double), cudaMemcpyHostToDevice);

    // initialize the gradient on the GPU with zero
    cudaMemset(cuda_grad_out, 0, n * n * sizeof(double));

    // for the functions we need theta in its exponential form
    array_exp<<<32, 64>>>(cuda_ptheta, n * n);

    // again check for errors
    // errors could occur if CUDA is not installed correctly or the kernel call did not work correctly
    if (cudaPeekAtLastError() != cudaSuccess)
    {
        // cast cudaError_t to int, not the best style, but simplest method to get it work in Cython
        return (int)cudaPeekAtLastError();
    }

    cuda_gradient_and_score_computation(cuda_ptheta, n, cuda_grad_out, cuda_pD, pth, q, tmp1, tmp2, cuda_score);

    // copy the results to the CPU
    cudaMemcpy(grad_out, cuda_grad_out, n * n * sizeof(double), cudaMemcpyDeviceToHost);
    cudaMemcpy(score_out, cuda_score, sizeof(double), cudaMemcpyDeviceToHost);

    // free all memory on the GPU
    cudaFree(d_memory);

    return (int)cudaGetLastError();
}

/**
 * this function computes the Fisher information matrix for the current MHN for a given observed frequency of tumors in data using CUDA
 *
 * @param[in] ptheta array containing the theta entries
 * @param[in] n number of genes considered by the MHN, also number of columns/rows of theta
 * @param[in] pD observed frequency of tumors in data
 * @param[out] grad_out array of size n*n in which the gradient will be stored
 * @param[out] score_out the marginal log-likelihood score is stored at this position
 *
 * @return CUDA error code converted to integer for better interoperability with Cython
 */
extern "C" int DLL_PREFIX cuda_fisher_upper(double *ptheta, int n, double *fim)
{

    int nx = 1 << n;
    // the arrays have to be at least of size MIN_BLOCK_NUM, else there will be errors when summing over arrays
    if (nx < MIN_BLOCK_NUM)
    {
        nx = MIN_BLOCK_NUM;
    }

    double *cuda_fim_out;
    double *pth, *zero_mask, *dg, *dQ_st, *dQ_ij, *masked_dQ_st, *q_st, *temp, *temp_score;
    double *cuda_ptheta;

    // allocate memory on the GPU
    // we allocate all at once so that we can easily check for allocation errors
    // if we did each allocation as a separate cudaMalloc, we would have to check for errors after each single call
    double *d_memory;
    cudaMalloc(&d_memory,
               n * n * n * n * sizeof(double) + // cuda_fim_out
                   nx * sizeof(double) +        // pth
                   nx * sizeof(double) +        // zero_mask
                   nx * sizeof(double) +        // dg
                   nx * sizeof(double) +        // dQ_st
                   nx * sizeof(double) +        // dQ_ij
                   nx * sizeof(double) +        // masked_dQ_st
                   nx * sizeof(double) +        // q_st
                   nx * sizeof(double) +        // temp
                   n * n * sizeof(double) +     // cuda_ptheta
                   1 * sizeof(double)           // temp_score
    );

    // check for errors
    // errors could occur if CUDA is not installed correctly or if the user tries to allocate too much memory
    if (cudaPeekAtLastError() != cudaSuccess)
    {
        // cast cudaError_t to int, not the best style, but simplest method to get it work in Cython
        return (int)cudaPeekAtLastError();
    }

    cuda_fim_out = d_memory;
    pth = d_memory + n * n * n * n;
    zero_mask = d_memory + n * n * n * n + nx;
    dg = d_memory + n * n * n * n + 2 * nx;
    dQ_st = d_memory + n * n * n * n + 3 * nx;
    dQ_ij = d_memory + n * n * n * n + 4 * nx;
    masked_dQ_st = d_memory + n * n * n * n + 5 * nx;
    q_st = d_memory + n * n * n * n + 6 * nx;
    temp = d_memory + n * n * n * n + 7 * nx;
    cuda_ptheta = d_memory + n * n * n * n + 8 * nx;
    temp_score = d_memory + n * n * n * n + 8 * nx + n * n;

    // copy theta to the GPU
    cudaMemcpy(cuda_ptheta, ptheta, n * n * sizeof(double), cudaMemcpyHostToDevice);

    // initialize the fim on the GPU with zero
    cudaMemset(cuda_fim_out, 0, n * n * n * n * sizeof(double));

    // for the functions we need theta in its exponential form
    array_exp<<<32, 64>>>(cuda_ptheta, n * n);

    // again check for errors
    // errors could occur if CUDA is not installed correctly or the kernel call did not work correctly
    if (cudaPeekAtLastError() != cudaSuccess)
    {
        // cast cudaError_t to int, not the best style, but simplest method to get it work in Cython
        return (int)cudaPeekAtLastError();
    }

    fisher_upper(cuda_ptheta, n, cuda_fim_out, pth, zero_mask, dg, dQ_st, dQ_ij, masked_dQ_st, q_st, temp, temp_score);

    // copy the results to the CPU
    cudaMemcpy(fim, cuda_fim_out, n * n * n * n * sizeof(double), cudaMemcpyDeviceToHost);

    // free all memory on the GPU
    cudaFree(d_memory);

    return (int)cudaGetLastError();
}

/**
 * computes the solution for [I-Q] x = b using forward and backward substitution
 *
 * @param[in] theta theta matrix representing the MHN with size n x n
 * @param[in] n number of rows and column of the theta matrix
 * @param[in] b vector of size 2^n which should be multiplied with [I-Q]^(-1)
 * @param[out] xout array of size 2^n which will contain the result of the matrix-vector multiplication at the end
 */
extern "C" void DLL_PREFIX gpu_compute_inverse(double *theta, int n, double *b, double *xout, bool transp = false)
{

    int nx = 1 << n;
    int block_num, thread_num;

    determine_block_thread_num(block_num, thread_num, n);

    double *d_theta;
    double *d_b, *d_xout;
    double *d_dg;

    cudaMalloc(&d_theta, n * n * sizeof(double));
    cudaMalloc(&d_xout, nx * sizeof(double));
    cudaMalloc(&d_dg, nx * sizeof(double));

    cudaMemcpy(d_theta, theta, n * n * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy(d_xout, b, nx * sizeof(double), cudaMemcpyHostToDevice);

    array_exp<<<32, 64>>>(d_theta, n * n);

    fill_array<<<block_num, thread_num>>>(d_dg, 1, nx);
    cuda_subtract_q_diag(d_theta, n, d_dg, block_num, thread_num);

    _compute_inverse(d_theta, n, d_dg, d_xout, transp);

    cudaMemcpy(xout, d_xout, nx * sizeof(double), cudaMemcpyDeviceToHost);

    cudaFree(d_theta);
    cudaFree(d_xout);
    cudaFree(d_dg);
}