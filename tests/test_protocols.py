"""
Unit tests for sliding window protocols and simulation engine.
"""

import unittest
from protocols.one_bit import OneBitProtocol
from protocols.go_back_n import GoBackNProtocol
from protocols.selective_repeat import SelectiveRepeatProtocol
from simulation.network import NetworkChannel
from simulation.simulator import Simulator


class TestProtocols(unittest.TestCase):
    def test_one_bit_no_loss(self):
        protocol = OneBitProtocol(num_frames=10, timeout=300.0)
        network = NetworkChannel(
            transmission_delay=100.0,
            ack_delay=50.0,
            packet_loss_pct=0.0,
            ack_loss_pct=0.0,
            seed=42,
        )
        sim = Simulator(protocol, network)
        metrics = sim.run()

        self.assertEqual(metrics.total_transmissions, 10)
        self.assertEqual(metrics.retransmissions, 0)
        self.assertEqual(metrics.packets_lost, 0)
        self.assertEqual(metrics.acks_received, 10)
        self.assertEqual(len(protocol.acked_frames), 10)

    def test_go_back_n_no_loss(self):
        protocol = GoBackNProtocol(num_frames=10, window_size=4, timeout=300.0)
        network = NetworkChannel(
            transmission_delay=100.0,
            ack_delay=50.0,
            packet_loss_pct=0.0,
            ack_loss_pct=0.0,
            seed=42,
        )
        sim = Simulator(protocol, network)
        metrics = sim.run()

        self.assertEqual(metrics.total_transmissions, 10)
        self.assertEqual(metrics.retransmissions, 0)
        self.assertEqual(metrics.packets_lost, 0)
        self.assertEqual(metrics.acks_received, 10)
        self.assertEqual(len(protocol.acked_frames), 10)

    def test_selective_repeat_no_loss(self):
        protocol = SelectiveRepeatProtocol(num_frames=10, window_size=4, timeout=300.0)
        network = NetworkChannel(
            transmission_delay=100.0,
            ack_delay=50.0,
            packet_loss_pct=0.0,
            ack_loss_pct=0.0,
            seed=42,
        )
        sim = Simulator(protocol, network)
        metrics = sim.run()

        self.assertEqual(metrics.total_transmissions, 10)
        self.assertEqual(metrics.retransmissions, 0)
        self.assertEqual(metrics.packets_lost, 0)
        self.assertEqual(metrics.acks_received, 10)
        self.assertEqual(len(protocol.acked_frames), 10)

    def test_loss_and_retransmissions(self):
        protocol = GoBackNProtocol(num_frames=10, window_size=4, timeout=300.0)
        network = NetworkChannel(
            transmission_delay=100.0,
            ack_delay=50.0,
            packet_loss_pct=20.0,
            ack_loss_pct=10.0,
            seed=123,
        )
        sim = Simulator(protocol, network)
        metrics = sim.run()

        self.assertGreater(metrics.total_transmissions, 10)
        self.assertGreater(metrics.retransmissions, 0)
        self.assertEqual(len(protocol.acked_frames), 10)

    def test_reproducibility_with_seed(self):
        p1 = SelectiveRepeatProtocol(num_frames=10, window_size=4, timeout=300.0)
        n1 = NetworkChannel(100.0, 50.0, 15.0, 10.0, seed=999)
        sim1 = Simulator(p1, n1)
        m1 = sim1.run()

        p2 = SelectiveRepeatProtocol(num_frames=10, window_size=4, timeout=300.0)
        n2 = NetworkChannel(100.0, 50.0, 15.0, 10.0, seed=999)
        sim2 = Simulator(p2, n2)
        m2 = sim2.run()

        self.assertEqual(m1.total_transmissions, m2.total_transmissions)
        self.assertEqual(m1.retransmissions, m2.retransmissions)
        self.assertEqual(m1.total_time_ms, m2.total_time_ms)

    def test_selective_repeat_selective_retransmission(self):
        # Verify SR retransmits fewer total packets than GBN under identical lost frame pattern
        gbn_protocol = GoBackNProtocol(num_frames=8, window_size=4, timeout=300.0)
        gbn_net = NetworkChannel(100.0, 50.0, 25.0, 15.0, seed=55)
        gbn_sim = Simulator(gbn_protocol, gbn_net)
        gbn_metrics = gbn_sim.run()

        sr_protocol = SelectiveRepeatProtocol(num_frames=8, window_size=4, timeout=300.0)
        sr_net = NetworkChannel(100.0, 50.0, 25.0, 15.0, seed=55)
        sr_sim = Simulator(sr_protocol, sr_net)
        sr_metrics = sr_sim.run()

        self.assertLessEqual(sr_metrics.retransmissions, gbn_metrics.retransmissions)

    def test_ack_loss_recovery(self):
        protocol = OneBitProtocol(num_frames=5, timeout=300.0)
        network = NetworkChannel(100.0, 50.0, packet_loss_pct=0.0, ack_loss_pct=50.0, seed=77)
        sim = Simulator(protocol, network)
        metrics = sim.run()

        self.assertEqual(len(protocol.acked_frames), 5)
        self.assertGreater(metrics.acks_lost, 0)


if __name__ == "__main__":
    unittest.main()
