"""This file contains unittests for model.py

author(s): Stefan Vocht, Y. Linda Hu"""


import unittest

import numpy as np

from mhn import model
from mhn.full_state_space import ModelConstruction, UtilityFunctions, Likelihood
from numpy.testing import assert_almost_equal as np_assert_almost_equal
from itertools import permutations


class TestMHN(unittest.TestCase):
    """
    Tests methods of the cMHN class.
    """

    def setUp(self) -> None:
        """
        Preparation for each test
        """
        np.random.seed(0)  # set random seed for reproducibility

    def test_sample_artificial_data(self):
        """
        Tests if the distribution sampled by sample_artificial_data() equals the distribution represented by the cMHN.
        """
        theta = ModelConstruction.random_theta(8)
        mhn_object = model.cMHN(theta)
        p_th = Likelihood.generate_pTh(theta)

        art_data = mhn_object.sample_artificial_data(500_000)
        p_data = UtilityFunctions.data_to_pD(art_data)
        np.testing.assert_allclose(p_th, p_data, atol=1e-3)

    def test_sample_trajectories(self):
        """
        Tests if the distribution sampled by sample_trajectories() equals the distribution represented by the cMHN.
        """
        n = 8
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta)
        p_th = Likelihood.generate_pTh(theta)

        trajectories, obs_times = mhn_object.sample_trajectories(500_000, [])
        cross_sec_data = list(map(
            lambda trajectory: [1 if i in trajectory else 0 for i in range(n)],
            trajectories
        ))
        cross_sec_data = np.array(cross_sec_data)
        p_data = UtilityFunctions.data_to_pD(cross_sec_data)
        np.testing.assert_allclose(p_th, p_data, atol=1e-3)

    def test_sample_trajectories_initial_state(self):
        """
        Tests if the initial state parameter works correctly.
        """
        n = 8
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta)
        mhn_object.events = ["A" * i for i in range(n)]

        initial_event_num = 2
        initial_bin_state = np.zeros(n, dtype=np.int32)
        initial_bin_state[:initial_event_num] = 1
        initial_event_state = ["A" * i for i in range(initial_event_num)]

        np.random.seed(0)
        trajectories_1, obs_times_1 = mhn_object.sample_trajectories(
            100, initial_state=initial_bin_state)
        np.random.seed(0)
        trajectories_2, obs_times_2 = mhn_object.sample_trajectories(
            100, initial_state=initial_event_state)

        np.testing.assert_array_equal(obs_times_1, obs_times_2)
        self.assertListEqual(trajectories_1, trajectories_2)

    def test_compute_marginal_likelihood(self):
        """
        Tests if the probabilities yielded by compute_marginal_likelihood() match the actual probability distribution.
        """
        n = 5
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta)

        p_th = Likelihood.generate_pTh(theta)

        # code from
        # https://stackoverflow.com/questions/22227595/convert-integer-to-binary-array-with-suitable-padding
        d = np.arange(2**n)
        all_possible_states = (
            (d[:, None] & (1 << np.arange(n))) > 0).astype(np.int32)

        for i in range(2**n):
            p = mhn_object.compute_marginal_likelihood(all_possible_states[i])
            self.assertAlmostEqual(p, p_th[i], 10)

    def test_compute_next_event_probs(self):
        """
        Tests if running compute_next_event_probs() raises an error and if probs sum up to 1.
        """
        n = 5
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta, events=["A"*(i+1) for i in range(n)])

        state = np.zeros(n, dtype=np.int32)
        state[0] = 1

        # Here the probabilities should sum up to 1, but an additional entry for the observation probability exists
        probs_df = mhn_object.compute_next_event_probs(state, True, True)
        print(probs_df)
        self.assertAlmostEqual(probs_df["PROBS"].sum(), 1., 10)
        self.assertEqual(len(probs_df), n + 1)

        # Here the probabilities should sum up to 1 as there is no observation event
        probs_df = mhn_object.compute_next_event_probs(state, True, False)
        self.assertAlmostEqual(probs_df["PROBS"].sum(), 1., 10)
        self.assertEqual(len(probs_df), n)

    def test_order_likelihood(self):
        """Tests if the order likelihood is computed correctly.
        """
        n = 5
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta)
        diag = mhn_object.get_restr_diag(state=np.ones(n, dtype=np.int32))

        order = [4, 3, 0]
        p = np.exp(theta[4, 4]) /\
            (1 - diag[0]) * \
            np.exp(theta[3, [3, 4]].sum()) /\
            (1 - diag[2 ** 4]) * \
            np.exp(theta[0, [0, 3, 4]].sum()) /\
            (1 - diag[2 ** 3 + 2 ** 4]) / \
            (1 - diag[2 ** 3 + 2 ** 4 + 2 ** 0])
        np_assert_almost_equal(mhn_object.order_likelihood(order), p)

    def test_likeliest_order_computation(self):
        """Tests if the likeliest order is computed correctly.
        """
        n = 5
        theta = ModelConstruction.random_theta(n)
        mhn_object = model.cMHN(theta)
        state = np.zeros(n, dtype=np.int32)
        state[[0, 3, 4]] = 1

        prob, order = mhn_object.likeliest_order(state)
        self.assertAlmostEqual(prob, mhn_object.order_likelihood(order))

        order = tuple(order)

        for other_order in permutations(order):
            if other_order == order:
                continue
            other_prob = mhn_object.order_likelihood(other_order)
            self.assertGreaterEqual(prob, other_prob)


class TestOmegaMHN(unittest.TestCase):
    """
    Tests methods of the oMHN class.
    """

    def setUp(self) -> None:
        """
        Preparation for each test.
        """
        np.random.seed(0)  # set random seed for reproducibility

    def test_sample_trajectories(self):
        """
        Tests if the distribution sampled by sample_trajectories() equals the distribution represented by the oMHN.
        """
        n = 8
        theta = ModelConstruction.random_theta(n)
        theta = np.vstack((theta, np.random.random(n)))
        mhn_object = model.oMHN(theta)
        p_th = Likelihood.generate_pTh(
            mhn_object.get_equivalent_classical_mhn().log_theta)

        trajectories, obs_times = mhn_object.sample_trajectories(500_000, [])
        cross_sec_data = list(map(
            lambda trajectory: [1 if i in trajectory else 0 for i in range(n)],
            trajectories
        ))
        cross_sec_data = np.array(cross_sec_data)
        p_data = UtilityFunctions.data_to_pD(cross_sec_data)
        np.testing.assert_allclose(p_th, p_data, atol=1e-3)

    def test_compute_next_event_probs(self):
        """
        Tests if running compute_next_event_probs() raises an error and if probs sum up to 1.
        """
        n = 5
        theta = ModelConstruction.random_theta(n)
        theta = np.vstack((theta, np.random.random(n)))
        mhn_object = model.oMHN(theta)

        state = np.zeros(n, dtype=np.int32)
        state[0] = 1

        # Here the probabilities should sum up to 1, but an additional entry for the observation probability exists
        probs_df = mhn_object.compute_next_event_probs(state, True, True)
        self.assertAlmostEqual(probs_df["PROBS"].sum(), 1., 10)
        self.assertEqual(len(probs_df), n + 1)

        # Here the probabilities should sum up to 1 as there is no observation event
        probs_df = mhn_object.compute_next_event_probs(state, True, False)
        self.assertAlmostEqual(probs_df["PROBS"].sum(), 1., 10)


if __name__ == '__main__':
    unittest.main()
