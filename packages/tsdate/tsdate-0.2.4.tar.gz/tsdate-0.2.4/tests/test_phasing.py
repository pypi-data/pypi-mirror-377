# MIT License
#
# Copyright (c) 2021-23 Tskit Developers
# Copyright (c) 2020-21 University of Oxford
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Test cases for the gamma-variational approximations in tsdate
"""

import msprime
import numpy as np
import pytest
import tsinfer
import tskit

import tsdate
from tsdate.phasing import (
    block_singletons,
    insert_unphased_singletons,
    mutation_frequency,
    remove_singletons,
    rephase_singletons,
)


@pytest.fixture(scope="session")
def inferred_ts():
    ts = msprime.sim_ancestry(
        10,
        population_size=1e4,
        recombination_rate=1e-8,
        sequence_length=1e6,
        random_seed=1,
    )
    ts = msprime.sim_mutations(ts, rate=1e-8, random_seed=1)
    sample_data = tsinfer.SampleData.from_tree_sequence(ts)
    inferred_ts = tsinfer.infer(sample_data).simplify()
    return inferred_ts


class TestBlockSingletons:
    @staticmethod
    def naive_block_singletons(ts, individual):
        """
        Get all intervals where the two intermediate parents of an individual are
        unchanged over the interval.
        """
        i = individual
        j, k = ts.individual(i).nodes
        last_block = np.full(2, tskit.NULL)
        last_span = np.zeros(2)
        muts_edges = np.full((ts.num_mutations, 2), tskit.NULL)
        blocks_edge = []
        blocks_span = []
        for tree in ts.trees():
            if tree.num_edges == 0:  # skip tree
                muts = []
                span = 0.0
                block = tskit.NULL, tskit.NULL
            else:
                muts = [m.id for m in tree.mutations() if m.node == j or m.node == k]
                span = tree.interval.span
                block = tree.edge(j), tree.edge(k)
                for m in muts:
                    muts_edges[m] = block
            if last_block[0] != tskit.NULL and not np.array_equal(
                block, last_block
            ):  # flush block
                blocks_edge.extend(last_block)
                blocks_span.extend(last_span)
                last_span[:] = 0.0
            last_span += len(muts), span
            last_block[:] = block
        if last_block[0] != tskit.NULL:  # flush last block
            blocks_edge.extend(last_block)
            blocks_span.extend(last_span)
        blocks_edge = np.array(blocks_edge).reshape(-1, 2)
        blocks_span = np.array(blocks_span).reshape(-1, 2)
        total_span = np.sum([t.interval.span for t in ts.trees() if t.num_edges > 0])
        total_muts = np.sum(np.logical_or(ts.mutations_node == j, ts.mutations_node == k))
        assert np.sum(blocks_span[:, 0]) == total_muts
        assert np.sum(blocks_span[:, 1]) == total_span
        return blocks_span, blocks_edge, muts_edges

    def test_against_naive(self, inferred_ts):
        """
        Test fast routine against simpler tree-by-tree,
        individual-by-individual implementation
        """
        ts = inferred_ts
        individuals_unphased = np.full(ts.num_individuals, False)
        unphased_individuals = np.arange(0, ts.num_individuals // 2)
        individuals_unphased[unphased_individuals] = True
        block_stats, block_edges, muts_block = block_singletons(ts, individuals_unphased)
        block_edges = block_edges
        singletons = muts_block != tskit.NULL
        muts_edges = np.full((ts.num_mutations, 2), tskit.NULL)
        muts_edges[singletons] = block_edges[muts_block[singletons]]
        ck_num_blocks = 0
        ck_num_singletons = 0
        for i in np.flatnonzero(individuals_unphased):
            ck_block_stats, ck_block_edges, ck_muts_edges = self.naive_block_singletons(
                ts, i
            )
            ck_num_blocks += ck_block_stats.shape[0]
            # blocks of individual i
            nodes_i = ts.individual(i).nodes
            blocks_i = np.isin(ts.edges_child[block_edges.min(axis=1)], nodes_i)
            np.testing.assert_allclose(block_stats[blocks_i], ck_block_stats)
            np.testing.assert_array_equal(
                np.min(block_edges[blocks_i], axis=1), np.min(ck_block_edges, axis=1)
            )
            np.testing.assert_array_equal(
                np.max(block_edges[blocks_i], axis=1), np.max(ck_block_edges, axis=1)
            )
            # singleton mutations in unphased individual i
            ck_muts_i = ck_muts_edges[:, 0] != tskit.NULL
            np.testing.assert_array_equal(
                np.min(muts_edges[ck_muts_i], axis=1),
                np.min(ck_muts_edges[ck_muts_i], axis=1),
            )
            np.testing.assert_array_equal(
                np.max(muts_edges[ck_muts_i], axis=1),
                np.max(ck_muts_edges[ck_muts_i], axis=1),
            )
            ck_num_singletons += np.sum(ck_muts_i)
        assert ck_num_blocks == block_stats.shape[0] == block_edges.shape[0]
        assert ck_num_singletons == np.sum(singletons)

    def test_total_counts(self, inferred_ts):
        """
        Sanity check: total number of mutations should equal number of singletons
        and total edge span should equal sum of spans of singleton edges
        """
        ts = inferred_ts
        individuals_unphased = np.full(ts.num_individuals, False)
        unphased_individuals = np.arange(0, ts.num_individuals // 2)
        individuals_unphased[unphased_individuals] = True
        unphased_nodes = np.concatenate(
            [ts.individual(i).nodes for i in unphased_individuals]
        )
        total_singleton_span = 0.0
        total_singleton_muts = 0.0
        for t in ts.trees():
            if t.num_edges == 0:
                continue
            for s in t.samples():
                if s in unphased_nodes:
                    total_singleton_span += t.span
            for m in t.mutations():
                if t.num_samples(m.node) == 1 and (m.node in unphased_nodes):
                    total_singleton_muts += 1.0
        block_stats, *_ = block_singletons(ts, individuals_unphased)
        assert np.isclose(np.sum(block_stats[:, 0]), total_singleton_muts)
        assert np.isclose(np.sum(block_stats[:, 1]), total_singleton_span / 2)

    def test_singleton_edges(self, inferred_ts):
        """
        Sanity check: all singleton edges attached to unphased individuals
        should show up in blocks
        """
        ts = inferred_ts
        individuals_unphased = np.full(ts.num_individuals, False)
        unphased_individuals = np.arange(0, ts.num_individuals // 2)
        individuals_unphased[unphased_individuals] = True
        unphased_nodes = set(
            np.concatenate([ts.individual(i).nodes for i in unphased_individuals])
        )
        ck_singleton_edge = set()
        for t in ts.trees():
            if t.num_edges == 0:
                continue
            for s in ts.samples():
                if s in unphased_nodes:
                    ck_singleton_edge.add(t.edge(s))
        _, block_edges, *_ = block_singletons(ts, individuals_unphased)
        singleton_edge = {i for i in block_edges.flatten()}
        assert singleton_edge == ck_singleton_edge

    def test_singleton_mutations(self, inferred_ts):
        """
        Sanity check: all singleton mutations in unphased individuals
        should show up in blocks
        """
        ts = inferred_ts
        individuals_unphased = np.full(ts.num_individuals, False)
        unphased_individuals = np.arange(0, ts.num_individuals // 2)
        individuals_unphased[unphased_individuals] = True
        unphased_nodes = np.concatenate(
            [ts.individual(i).nodes for i in unphased_individuals]
        )
        ck_singleton_muts = set()
        for t in ts.trees():
            if t.num_edges == 0:
                continue
            for m in t.mutations():
                if t.num_samples(m.node) == 1 and (m.node in unphased_nodes):
                    ck_singleton_muts.add(m.id)
        _, _, block_muts = block_singletons(ts, individuals_unphased)
        singleton_muts = {i for i in np.flatnonzero(block_muts != tskit.NULL)}
        assert singleton_muts == ck_singleton_muts

    def test_all_phased(self, inferred_ts):
        """
        Test that empty arrays are returned when all individuals are phased
        """
        ts = inferred_ts
        individuals_unphased = np.full(ts.num_individuals, False)
        block_stats, block_edges, block_muts = block_singletons(ts, individuals_unphased)
        assert block_stats.shape == (0, 2)
        assert block_edges.shape == (0, 2)
        assert np.all(block_muts == tskit.NULL)


class TestPhaseAgnosticDating:
    """
    If singleton phase is randomized, we should get same results with the phase
    agnostic algorithm
    """

    def test_phase_invariance(self, inferred_ts):
        ts1 = inferred_ts
        ts2 = rephase_singletons(ts1, use_node_times=False, random_seed=1)
        frq = mutation_frequency(ts1)
        assert np.all(ts1.mutations_node[frq != 1] == ts2.mutations_node[frq != 1])
        assert np.any(ts1.mutations_node[frq == 1] != ts2.mutations_node[frq == 1])
        dts1 = tsdate.date(
            ts1,
            mutation_rate=1.29e-8,
            method="variational_gamma",
            singletons_phased=False,
        )
        dts2 = tsdate.date(
            ts2,
            mutation_rate=1.29e-8,
            method="variational_gamma",
            singletons_phased=False,
        )
        np.testing.assert_allclose(dts1.nodes_time, dts2.nodes_time)
        np.testing.assert_allclose(dts1.mutations_node, dts2.mutations_node)
        np.testing.assert_allclose(dts1.mutations_time, dts2.mutations_time)

    def test_not_phase_invariance(self, inferred_ts):
        ts1 = inferred_ts
        ts2 = rephase_singletons(ts1, use_node_times=False, random_seed=1)
        frq = mutation_frequency(ts1)
        assert np.all(ts1.mutations_node[frq != 1] == ts2.mutations_node[frq != 1])
        assert np.any(ts1.mutations_node[frq == 1] != ts2.mutations_node[frq == 1])
        dts1 = tsdate.date(
            ts1,
            mutation_rate=1.29e-8,
            method="variational_gamma",
            singletons_phased=True,
        )
        dts2 = tsdate.date(
            ts2,
            mutation_rate=1.29e-8,
            method="variational_gamma",
            singletons_phased=True,
        )
        assert not np.allclose(dts1.nodes_time, dts2.nodes_time)
        assert not np.allclose(dts1.mutations_node, dts2.mutations_node)
        assert not np.allclose(dts1.mutations_time, dts2.mutations_time)


class TestMutationFrequency:
    @staticmethod
    def naive_mutation_frequency(ts, sample_set):
        frq = np.zeros(ts.num_mutations)
        for t in ts.trees():
            for m in t.mutations():
                for s in t.samples(m.node):
                    frq[m.id] += int(s in sample_set)
        return frq

    def test_mutation_frequency(self, inferred_ts):
        ck_freq = self.naive_mutation_frequency(inferred_ts, inferred_ts.samples())
        freq = mutation_frequency(inferred_ts)
        np.testing.assert_array_equal(ck_freq, freq.squeeze())

    def test_mutation_frequency_stratified(self, inferred_ts):
        sample_sets = [
            list(np.arange(5)),
            list(np.arange(3, 10)),
            list(np.arange(15, 20)),
        ]
        freqs = mutation_frequency(inferred_ts, sample_sets)
        for i, s in enumerate(sample_sets):
            ck_freq = self.naive_mutation_frequency(inferred_ts, s)
            np.testing.assert_array_equal(ck_freq, freqs[:, i])


class TestModifySingletons:
    def test_remove_singletons(self, inferred_ts):
        new_ts, _ = remove_singletons(inferred_ts)
        old_frq = mutation_frequency(inferred_ts)
        new_frq = mutation_frequency(new_ts)
        num_singletons = np.sum(old_frq == 1)
        assert inferred_ts.num_mutations - num_singletons == new_ts.num_mutations
        assert np.any(old_frq == 1)
        assert np.all(new_frq > 1)

    def test_insert_unphased_singletons(self, inferred_ts):
        its = inferred_ts
        inter_ts, removed = remove_singletons(its)
        new_ts = insert_unphased_singletons(inter_ts, *removed)
        assert new_ts.num_mutations == its.num_mutations
        old_pos = its.sites_position[its.mutations_site]
        old_ind = its.nodes_individual[its.mutations_node]
        old_order = np.argsort(old_pos)
        new_pos = new_ts.sites_position[new_ts.mutations_site]
        new_ind = new_ts.nodes_individual[new_ts.mutations_node]
        new_order = np.argsort(new_pos)
        np.testing.assert_array_equal(
            old_pos[old_order],
            new_pos[new_order],
        )
        np.testing.assert_array_equal(
            old_ind[old_order],
            new_ind[new_order],
        )
        # TODO: more thorough testing (ancestral state, etc)
