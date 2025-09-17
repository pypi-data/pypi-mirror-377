"""
This file contains unit tests for the full state-space functions of the mhn package.
"""
# author: Stefan Vocht

import unittest
import numpy as np

import mhn
from mhn.training import likelihood_cmhn
from mhn.full_state_space import Likelihood, ModelConstruction, PerformanceCriticalCode


class TestCudaGradient(unittest.TestCase):
    """
    Tests for the function cuda_gradient_and_score
    """
    def setUp(self) -> None:
        """
        Preparation for each test
        """
        np.random.seed(0)  # set random seed for reproducibility
        if mhn.cuda_available() != mhn.CUDA_AVAILABLE:
            self.skipTest("CUDA not available for testing")

    def test_compare_with_cython(self):
        """
        Compare the full state-space score and gradient of the CUDA implementation with those of the Cython implementation
        """
        n = 4
        theta = ModelConstruction.random_theta(n)
        pD = np.random.random(2**n)
        pD /= pD.sum()
        gradient1 = Likelihood.grad(theta, pD)
        score1 = Likelihood.score(theta, pD)
        gradient2, score2 = Likelihood.cuda_gradient_and_score(theta, pD)
        self.assertEqual(round(score1, 8), round(score2, 8))
        print(score1, score2)
        print(gradient2)
        np.testing.assert_array_equal(np.around(gradient1, decimals=8), np.around(gradient2, decimals=8))

    def test_forward_substitution(self):
        """
        Test the computation of [I-Q]^(-1) b of the CUDA implementation with the Cython implementation
        """
        n = 3
        theta = ModelConstruction.random_theta(n)
        pD = np.random.random(2**n)
        pD /= pD.sum()

        res1 = Likelihood.cuda_compute_inverse(theta, pD)
        dg = 1 - ModelConstruction.q_diag(theta)
        res2 = np.empty(2**n)
        PerformanceCriticalCode.compute_inverse(theta, dg, pD, res2, False)

        print(res1)
        print(res2)


if __name__ == '__main__':
    unittest.main()
