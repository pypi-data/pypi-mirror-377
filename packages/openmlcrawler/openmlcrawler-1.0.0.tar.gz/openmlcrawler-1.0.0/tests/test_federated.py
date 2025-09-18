"""
Test Federated Learning Module

Tests for federated learning coordinator, secure aggregation, and client functionality.
"""

import pytest
import numpy as np
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from openmlcrawler.core.federated import (
    FederatedCoordinator, FederatedClient, SecureAggregator,
    FederatedConfig, FederatedNode, ModelUpdate,
    create_federated_coordinator, create_federated_client,
    load_federated_config
)


class TestFederatedConfig:
    """Test FederatedConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FederatedConfig()
        assert config.coordinator_host == "localhost"
        assert config.coordinator_port == 8080
        assert config.num_rounds == 10
        assert config.min_clients == 3
        assert config.max_clients == 10
        assert config.aggregation_method == "fedavg"
        assert config.secure_aggregation is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = FederatedConfig(
            coordinator_host="192.168.1.100",
            coordinator_port=9000,
            num_rounds=5,
            min_clients=2,
            max_clients=5
        )
        assert config.coordinator_host == "192.168.1.100"
        assert config.coordinator_port == 9000
        assert config.num_rounds == 5
        assert config.min_clients == 2
        assert config.max_clients == 5


class TestModelUpdate:
    """Test ModelUpdate dataclass and serialization."""

    def test_model_update_creation(self):
        """Test creating a ModelUpdate instance."""
        model_weights = {
            'layer1': np.array([[1.0, 2.0], [3.0, 4.0]]),
            'layer2': np.array([5.0, 6.0, 7.0])
        }

        update = ModelUpdate(
            client_id="client_1",
            round_number=1,
            model_weights=model_weights,
            num_samples=100,
            timestamp=datetime.now(),
            checksum="test_checksum"
        )

        assert update.client_id == "client_1"
        assert update.round_number == 1
        assert update.num_samples == 100
        assert isinstance(update.timestamp, datetime)

    def test_model_update_serialization(self):
        """Test ModelUpdate serialization and deserialization."""
        model_weights = {
            'layer1': np.array([[1.0, 2.0], [3.0, 4.0]]),
            'layer2': np.array([5.0, 6.0, 7.0])
        }

        original_update = ModelUpdate(
            client_id="client_1",
            round_number=1,
            model_weights=model_weights,
            num_samples=100,
            timestamp=datetime.now(),
            checksum="test_checksum"
        )

        # Serialize to dict
        data = original_update.to_dict()

        # Deserialize from dict
        restored_update = ModelUpdate.from_dict(data)

        assert restored_update.client_id == original_update.client_id
        assert restored_update.round_number == original_update.round_number
        assert restored_update.num_samples == original_update.num_samples

        # Check model weights are restored correctly
        for layer_name in model_weights.keys():
            np.testing.assert_array_equal(
                restored_update.model_weights[layer_name],
                original_update.model_weights[layer_name]
            )


class TestSecureAggregator:
    """Test SecureAggregator functionality."""

    def test_aggregator_creation(self):
        """Test creating a SecureAggregator instance."""
        config = FederatedConfig()
        aggregator = SecureAggregator(config)

        assert aggregator.config == config
        assert aggregator.round_updates == {}

    def test_add_update(self):
        """Test adding model updates to aggregator."""
        config = FederatedConfig()
        aggregator = SecureAggregator(config)

        model_weights = {'layer1': np.array([1.0, 2.0, 3.0])}
        update = ModelUpdate(
            client_id="client_1",
            round_number=1,
            model_weights=model_weights,
            num_samples=100,
            timestamp=datetime.now(),
            checksum="test_checksum"
        )

        aggregator.add_update(update)

        assert 1 in aggregator.round_updates
        assert len(aggregator.round_updates[1]) == 1
        assert aggregator.round_updates[1][0] == update

    def test_can_aggregate_insufficient_updates(self):
        """Test can_aggregate with insufficient updates."""
        config = FederatedConfig(min_clients=3)
        aggregator = SecureAggregator(config)

        # Add only 2 updates
        for i in range(2):
            model_weights = {'layer1': np.array([1.0, 2.0, 3.0])}
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100,
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)

        assert not aggregator.can_aggregate(1)

    def test_can_aggregate_sufficient_updates(self):
        """Test can_aggregate with sufficient updates."""
        config = FederatedConfig(min_clients=3)
        aggregator = SecureAggregator(config)

        # Add 3 updates
        for i in range(3):
            model_weights = {'layer1': np.array([1.0, 2.0, 3.0])}
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100,
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)

        assert aggregator.can_aggregate(1)

    def test_aggregate_single_layer(self):
        """Test FedAvg aggregation with single layer."""
        config = FederatedConfig(min_clients=2)
        aggregator = SecureAggregator(config)

        # Create updates with different weights
        updates = []
        for i in range(2):
            model_weights = {'layer1': np.array([float(i+1), float(i+2), float(i+3)])}
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100,  # Same sample count for simplicity
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)
            updates.append(update)

        # Perform aggregation
        result = aggregator.aggregate(1)

        # Expected: weighted average = ([1,2,3] + [2,3,4]) / 2 = [1.5, 2.5, 3.5]
        expected = np.array([1.5, 2.5, 3.5])
        np.testing.assert_array_almost_equal(result['layer1'], expected)

    def test_aggregate_multiple_layers(self):
        """Test FedAvg aggregation with multiple layers."""
        config = FederatedConfig(min_clients=2)
        aggregator = SecureAggregator(config)

        # Create updates with multiple layers
        for i in range(2):
            model_weights = {
                'layer1': np.array([float(i+1), float(i+2)]),
                'layer2': np.array([float(i+3), float(i+4), float(i+5)])
            }
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100,
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)

        # Perform aggregation
        result = aggregator.aggregate(1)

        # Check both layers
        expected_layer1 = np.array([1.5, 2.5])
        expected_layer2 = np.array([3.5, 4.5, 5.5])

        np.testing.assert_array_almost_equal(result['layer1'], expected_layer1)
        np.testing.assert_array_almost_equal(result['layer2'], expected_layer2)

    def test_aggregate_weighted_by_samples(self):
        """Test FedAvg aggregation with different sample counts."""
        config = FederatedConfig(min_clients=2)
        aggregator = SecureAggregator(config)

        # Client 1: 100 samples, weights = [1, 2, 3]
        model_weights_1 = {'layer1': np.array([1.0, 2.0, 3.0])}
        update_1 = ModelUpdate(
            client_id="client_1",
            round_number=1,
            model_weights=model_weights_1,
            num_samples=100,
            timestamp=datetime.now(),
            checksum="checksum_1"
        )
        aggregator.add_update(update_1)

        # Client 2: 200 samples, weights = [4, 5, 6]
        model_weights_2 = {'layer1': np.array([4.0, 5.0, 6.0])}
        update_2 = ModelUpdate(
            client_id="client_2",
            round_number=1,
            model_weights=model_weights_2,
            num_samples=200,
            timestamp=datetime.now(),
            checksum="checksum_2"
        )
        aggregator.add_update(update_2)

        # Perform aggregation
        result = aggregator.aggregate(1)

        # Expected: (100*[1,2,3] + 200*[4,5,6]) / 300 = [900, 1200, 1500] / 300 = [3, 4, 5]
        expected = np.array([3.0, 4.0, 5.0])
        np.testing.assert_array_almost_equal(result['layer1'], expected)

    def test_get_round_stats(self):
        """Test getting round statistics."""
        config = FederatedConfig()
        aggregator = SecureAggregator(config)

        # Add some updates
        for i in range(3):
            model_weights = {'layer1': np.array([1.0, 2.0, 3.0])}
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100 + i * 50,
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)

        stats = aggregator.get_round_stats(1)

        assert stats['round_number'] == 1
        assert stats['num_updates'] == 3
        assert stats['total_samples'] == 450  # 100 + 150 + 200
        assert len(stats['clients']) == 3
        assert 'client_0' in stats['clients']


class TestFederatedCoordinator:
    """Test FederatedCoordinator functionality."""

    def test_coordinator_creation(self):
        """Test creating a FederatedCoordinator instance."""
        config = FederatedConfig()
        coordinator = FederatedCoordinator(config)

        assert coordinator.config == config
        assert coordinator.nodes == {}
        assert coordinator.current_round == 0
        assert not coordinator.is_running
        assert coordinator.global_model is None

    @pytest.mark.asyncio
    async def test_register_node(self):
        """Test registering a node with the coordinator."""
        config = FederatedConfig()
        coordinator = FederatedCoordinator(config)

        node = FederatedNode(
            node_id="test_node",
            host="localhost",
            port=8081,
            dataset_info={"name": "test_dataset", "size": 1000}
        )

        result = await coordinator.register_node(node)

        assert result is True
        assert "test_node" in coordinator.nodes
        assert coordinator.nodes["test_node"] == node

    def test_get_training_status(self):
        """Test getting training status."""
        config = FederatedConfig(num_rounds=5)
        coordinator = FederatedCoordinator(config)

        status = coordinator.get_training_status()

        assert not status['is_running']
        assert status['current_round'] == 0
        assert status['total_rounds'] == 5
        assert status['num_nodes'] == 0
        assert not status['global_model_available']

    @pytest.mark.asyncio
    async def test_stop_training(self):
        """Test stopping training."""
        config = FederatedConfig()
        coordinator = FederatedCoordinator(config)
        coordinator.is_running = True

        await coordinator.stop_training()

        assert not coordinator.is_running


class TestFederatedClient:
    """Test FederatedClient functionality."""

    def test_client_creation(self):
        """Test creating a FederatedClient instance."""
        client = FederatedClient("test_client", "localhost", 8080)

        assert client.node_id == "test_client"
        assert client.coordinator_host == "localhost"
        assert client.coordinator_port == 8080
        assert client.local_model is None
        assert not client.is_registered

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        client = FederatedClient("test_client")

        model_weights = {
            'layer1': np.array([[1.0, 2.0], [3.0, 4.0]]),
            'layer2': np.array([5.0, 6.0])
        }

        checksum = client._calculate_checksum(model_weights)

        # Checksum should be a string
        assert isinstance(checksum, str)
        assert len(checksum) > 0

        # Same weights should produce same checksum
        checksum2 = client._calculate_checksum(model_weights)
        assert checksum == checksum2

        # Different weights should produce different checksum
        different_weights = {'layer1': np.array([[1.1, 2.0], [3.0, 4.0]])}
        checksum3 = client._calculate_checksum(different_weights)
        assert checksum != checksum3


class TestFederatedConvenienceFunctions:
    """Test convenience functions for federated learning."""

    def test_create_federated_coordinator(self):
        """Test creating coordinator via convenience function."""
        config = FederatedConfig()
        coordinator = create_federated_coordinator(config)

        assert isinstance(coordinator, FederatedCoordinator)
        assert coordinator.config == config

    def test_create_federated_client(self):
        """Test creating client via convenience function."""
        client = create_federated_client("test_client", "localhost", 8080)

        assert isinstance(client, FederatedClient)
        assert client.node_id == "test_client"
        assert client.coordinator_host == "localhost"
        assert client.coordinator_port == 8080


class TestFederatedNode:
    """Test FederatedNode dataclass."""

    def test_node_creation(self):
        """Test creating a FederatedNode instance."""
        node = FederatedNode(
            node_id="test_node",
            host="localhost",
            port=8081,
            dataset_info={"name": "test_dataset", "size": 1000}
        )

        assert node.node_id == "test_node"
        assert node.host == "localhost"
        assert node.port == 8081
        assert node.dataset_info == {"name": "test_dataset", "size": 1000}
        assert node.status == "idle"
        assert node.capabilities == ["training", "inference"]

    def test_node_custom_capabilities(self):
        """Test node with custom capabilities."""
        node = FederatedNode(
            node_id="test_node",
            host="localhost",
            port=8081,
            dataset_info={"name": "test_dataset", "size": 1000},
            capabilities=["inference"]
        )

        assert node.capabilities == ["inference"]


# Integration tests
class TestFederatedIntegration:
    """Integration tests for federated learning components."""

    @pytest.mark.asyncio
    async def test_coordinator_node_registration(self):
        """Test coordinator registering multiple nodes."""
        config = FederatedConfig()
        coordinator = FederatedCoordinator(config)

        nodes = []
        for i in range(3):
            node = FederatedNode(
                node_id=f"node_{i}",
                host=f"192.168.1.{100+i}",
                port=8081 + i,
                dataset_info={"name": f"dataset_{i}", "size": 1000 + i * 100}
            )
            nodes.append(node)
            await coordinator.register_node(node)

        assert len(coordinator.nodes) == 3
        for node in nodes:
            assert node.node_id in coordinator.nodes

    def test_secure_aggregation_workflow(self):
        """Test complete secure aggregation workflow."""
        config = FederatedConfig(min_clients=2)
        aggregator = SecureAggregator(config)

        # Simulate 3 clients sending updates
        for i in range(3):
            model_weights = {
                'weights': np.array([1.0 + i, 2.0 + i]),
                'bias': np.array([0.1 + i * 0.1])
            }
            update = ModelUpdate(
                client_id=f"client_{i}",
                round_number=1,
                model_weights=model_weights,
                num_samples=100,
                timestamp=datetime.now(),
                checksum=f"checksum_{i}"
            )
            aggregator.add_update(update)

        # Check aggregation is possible
        assert aggregator.can_aggregate(1)

        # Perform aggregation
        result = aggregator.aggregate(1)

        # Verify result structure
        assert 'weights' in result
        assert 'bias' in result

        # Verify result values (weighted average)
        expected_weights = np.array([2.0, 3.0])  # ([1,2] + [2,3] + [3,4]) / 3
        expected_bias = np.array([0.2])  # ([0.1] + [0.2] + [0.3]) / 3

        np.testing.assert_array_almost_equal(result['weights'], expected_weights)
        np.testing.assert_array_almost_equal(result['bias'], expected_bias)