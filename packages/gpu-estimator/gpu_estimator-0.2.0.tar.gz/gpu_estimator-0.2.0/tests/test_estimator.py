"""
Tests for the GPU estimator functionality.
"""
import pytest
import math
from gpu_estimator import GPUEstimator, EstimationResult


class TestGPUEstimator:
    """Test the GPUEstimator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = GPUEstimator()

    def test_basic_estimation(self):
        """Test basic GPU estimation without dataset size."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            precision="fp16",
            gpu_type="A100"
        )

        assert isinstance(result, EstimationResult)
        assert result.num_gpus >= 1
        assert result.memory_per_gpu_gb > 0
        assert result.total_memory_gb > 0
        assert result.model_memory_gb > 0
        assert result.estimated_training_hours is None  # No dataset size provided

    def test_estimation_with_dataset(self):
        """Test GPU estimation with dataset size for training time calculation."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            dataset_size=50000,
            epochs=3,
            gpu_type="A100"
        )

        assert isinstance(result, EstimationResult)
        assert result.num_gpus >= 1
        assert result.estimated_training_hours is not None
        assert result.total_steps == 37500  # (50000/4) * 3
        assert result.steps_per_epoch == 12500  # 50000/4
        assert result.estimated_cost_usd is not None
        assert result.estimated_cost_usd > 0

    def test_gpu_memory_sizes(self):
        """Test that all supported GPU types have memory sizes."""
        expected_gpus = [
            "V100", "A100", "H100", "B200", "RTX3090", "RTX4090",
            "T4", "L4", "L40", "A40", "A6000"
        ]

        for gpu in expected_gpus:
            assert gpu in self.estimator.gpu_memory_sizes
            assert self.estimator.gpu_memory_sizes[gpu] > 0

    def test_b200_gpu_support(self):
        """Test that B200 GPU is properly supported."""
        assert "B200" in self.estimator.gpu_memory_sizes
        assert self.estimator.gpu_memory_sizes["B200"] == 192
        assert "B200" in self.estimator.gpu_hourly_rates
        assert self.estimator.gpu_hourly_rates["B200"] > 0

        # Test estimation with B200
        result = self.estimator.estimate(
            model_params=70e9,  # Large model for B200
            batch_size=8,
            gpu_type="B200"
        )

        assert result.num_gpus >= 1
        assert result.memory_per_gpu_gb <= 192 * 0.9  # With buffer

    def test_different_precisions(self):
        """Test estimation with different precision settings."""
        model_params = 7e9
        batch_size = 4

        fp32_result = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            precision="fp32",
            gpu_type="A100"
        )

        fp16_result = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            precision="fp16",
            gpu_type="A100"
        )

        # FP32 should require more memory than FP16
        assert fp32_result.total_memory_gb > fp16_result.total_memory_gb
        assert fp32_result.model_memory_gb > fp16_result.model_memory_gb

    def test_gradient_checkpointing(self):
        """Test that gradient checkpointing reduces memory usage."""
        model_params = 7e9
        batch_size = 4

        without_gc = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            gradient_checkpointing=False,
            gpu_type="A100"
        )

        with_gc = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            gradient_checkpointing=True,
            gpu_type="A100"
        )

        # Gradient checkpointing should reduce activation memory
        assert with_gc.activation_memory_gb < without_gc.activation_memory_gb
        assert with_gc.total_memory_gb < without_gc.total_memory_gb

    def test_optimizer_types(self):
        """Test different optimizer types affect memory usage."""
        model_params = 7e9
        batch_size = 4

        adam_result = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            optimizer="adam",
            precision="fp16",
            gpu_type="A100"
        )

        sgd_result = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            optimizer="sgd",
            precision="fp16",
            gpu_type="A100"
        )

        # Adam should require more memory than SGD
        assert adam_result.optimizer_memory_gb > sgd_result.optimizer_memory_gb
        assert adam_result.total_memory_gb > sgd_result.total_memory_gb

    def test_throughput_estimation(self):
        """Test throughput estimation for different model sizes and GPUs."""
        # Small model should have higher throughput
        small_throughput = self.estimator._estimate_throughput(
            model_params=1e9,
            batch_size=8,
            sequence_length=2048,
            gpu_type="A100"
        )

        # Large model should have lower throughput
        large_throughput = self.estimator._estimate_throughput(
            model_params=70e9,
            batch_size=8,
            sequence_length=2048,
            gpu_type="A100"
        )

        assert small_throughput > large_throughput

        # H100 should be faster than V100
        h100_throughput = self.estimator._estimate_throughput(
            model_params=7e9,
            batch_size=8,
            sequence_length=2048,
            gpu_type="H100"
        )

        v100_throughput = self.estimator._estimate_throughput(
            model_params=7e9,
            batch_size=8,
            sequence_length=2048,
            gpu_type="V100"
        )

        assert h100_throughput > v100_throughput

    def test_cost_estimation(self):
        """Test cost estimation functionality."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            dataset_size=50000,
            epochs=3,
            gpu_type="A100"
        )

        # Test standalone cost estimation
        standalone_cost = self.estimator.estimate_cost(
            result=result,
            gpu_type="A100"
        )

        assert standalone_cost == result.estimated_cost_usd
        assert standalone_cost > 0

        # Test with custom hourly rate
        custom_cost = self.estimator.estimate_cost(
            result=result,
            hourly_rate=10.0
        )

        expected_cost = result.estimated_training_hours * result.num_gpus * 10.0
        assert abs(custom_cost - expected_cost) < 0.01

    def test_batch_size_scaling(self):
        """Test that larger batch sizes increase memory usage."""
        model_params = 7e9

        small_batch = self.estimator.estimate(
            model_params=model_params,
            batch_size=2,
            gpu_type="A100"
        )

        large_batch = self.estimator.estimate(
            model_params=model_params,
            batch_size=8,
            gpu_type="A100"
        )

        # Larger batch should use more activation memory
        assert large_batch.activation_memory_gb > small_batch.activation_memory_gb
        assert large_batch.total_memory_gb > small_batch.total_memory_gb

    def test_sequence_length_scaling(self):
        """Test that longer sequences increase memory usage."""
        model_params = 7e9
        batch_size = 4

        short_seq = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            sequence_length=1024,
            gpu_type="A100"
        )

        long_seq = self.estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            sequence_length=4096,
            gpu_type="A100"
        )

        # Longer sequences should use more activation memory
        assert long_seq.activation_memory_gb > short_seq.activation_memory_gb
        assert long_seq.total_memory_gb > short_seq.total_memory_gb

    def test_estimation_result_to_dict(self):
        """Test EstimationResult to_dict method."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            dataset_size=50000,
            epochs=3,
            gpu_type="A100"
        )

        result_dict = result.to_dict()

        expected_keys = [
            "memory_per_gpu_gb", "num_gpus", "total_memory_gb",
            "model_memory_gb", "optimizer_memory_gb", "activation_memory_gb",
            "gradient_memory_gb", "efficiency_ratio", "estimated_training_hours",
            "total_steps", "steps_per_epoch", "estimated_cost_usd"
        ]

        for key in expected_keys:
            assert key in result_dict

        assert isinstance(result_dict, dict)
        assert result_dict["num_gpus"] == result.num_gpus
        assert result_dict["estimated_training_hours"] == result.estimated_training_hours


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = GPUEstimator()

    def test_very_small_model(self):
        """Test estimation with very small models."""
        result = self.estimator.estimate(
            model_params=1e6,  # 1M parameters
            batch_size=1,
            gpu_type="T4"
        )

        assert result.num_gpus == 1  # Should fit on one GPU
        assert result.total_memory_gb > 0

    def test_very_large_model(self):
        """Test estimation with very large models."""
        result = self.estimator.estimate(
            model_params=175e9,  # 175B parameters
            batch_size=1,
            gpu_type="A100"
        )

        assert result.num_gpus > 1  # Should require multiple GPUs
        assert result.total_memory_gb > 80  # Should exceed single GPU memory

    def test_custom_gpu_memory(self):
        """Test estimation with custom GPU memory."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            gpu_memory_gb=40.0,  # Custom 40GB GPU
            gpu_type=None
        )

        assert result.num_gpus >= 1
        assert result.memory_per_gpu_gb <= 40.0 * 0.9

    def test_zero_dataset_size(self):
        """Test that zero dataset size doesn't break estimation."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            dataset_size=0,
            gpu_type="A100"
        )

        assert result.estimated_training_hours is not None
        assert result.total_steps == 0
        assert result.steps_per_epoch == 0

    def test_cost_estimation_without_training_time(self):
        """Test that cost estimation fails gracefully without training time."""
        result = self.estimator.estimate(
            model_params=7e9,
            batch_size=4,
            gpu_type="A100"
        )

        with pytest.raises(ValueError, match="Training time not calculated"):
            self.estimator.estimate_cost(result)


if __name__ == "__main__":
    pytest.main([__file__])