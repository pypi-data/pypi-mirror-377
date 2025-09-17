#ifndef CUDA_INVERSE_BY_SUBSTITUTION_H_
#define CUDA_INVERSE_BY_SUBSTITUTION_H_

// on Windows we need to add a prefix in front of the function we want to use in other code
// on Linux this is not needed, so we define DLL_PREFIX depending on which os this code is compiled on
#ifdef _WIN32
#define DLL_PREFIX __declspec(dllexport)
#else
#define DLL_PREFIX 
#endif


// small function to compute n over k
int compute_binom_coef(int n, int k);


/**
 * Internal function to compute the solution for [I-Q] x = b using forward and backward substitution
 * All arrays given to this function must be allocated using cudaMalloc()!
 * 
 * @param[in] theta theta matrix representing the cMHN with size n x n
 * @param[in] n number of rows and columns of the theta matrix
 * @param[in] dg diagonal of [I-Q], you could also use a different diagonal to compute the inverse for a matrix that only differs in the diagonal from [I-Q]
 * @param[in, out] xout this vector of size 2^n must contain b at the beginning at will contain x at the end
 * @param[in] transp if set to true, computes the solution for [I-Q]^T x = b
*/
extern "C"  void DLL_PREFIX _compute_inverse(const double * __restrict__ theta, const int n, const double * __restrict__ dg, double * __restrict__ xout, bool transp);


#endif