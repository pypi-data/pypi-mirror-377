# by Stefan Vocht
#
# this file acts as a header file for PerformanceCriticalCode.pyx
#


cdef void internal_kron_vec(double[:, :] theta_mat, int i, double[:] x_vec, double *pout, bint diag, bint transp)

cdef void loop_j(int i, int n, double *pr, double *pg)

cpdef compute_inverse(double[:, :] theta, double[:] dg, double[:] b, double[:] xout, bint transp)

cdef void _compute_inverse(const double *theta, int n, const double *dg, const double *b, double *xout)

cdef void _compute_inverse_t(const double *theta, int n, const double *dg, const double *b, double *xout)
