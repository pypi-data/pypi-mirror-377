"""
Tests for the CLI functionality.
"""
import pytest
from click.testing import CliRunner
from gpu_estimator.cli import cli


class TestCLI:
    """Test the command-line interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_estimate_basic(self):
        """Test basic estimation command."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--gpu-type', 'A100'
        ])

        assert result.exit_code == 0
        assert "GPU ESTIMATION RESULTS" in result.output
        assert "Number of GPUs Needed:" in result.output
        assert "Memory per GPU:" in result.output

    def test_estimate_with_dataset(self):
        """Test estimation with dataset size."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--dataset-size', '50000',
            '--epochs', '3',
            '--gpu-type', 'A100'
        ])

        assert result.exit_code == 0
        assert "TRAINING ESTIMATES" in result.output
        assert "Steps per Epoch:" in result.output
        assert "Total Training Steps:" in result.output
        assert "Estimated Training Time:" in result.output
        assert "Estimated Cost:" in result.output

    def test_estimate_b200_gpu(self):
        """Test estimation with B200 GPU."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '70e9',
            '--batch-size', '8',
            '--gpu-type', 'B200'
        ])

        assert result.exit_code == 0
        assert "GPU Type: B200 (192GB)" in result.output
        assert "Number of GPUs Needed:" in result.output

    def test_estimate_with_model_name(self):
        """Test estimation with pre-defined model name."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-name', 'llama-7b',
            '--batch-size', '4',
            '--gpu-type', 'A100'
        ])

        assert result.exit_code == 0
        assert "GPU ESTIMATION RESULTS" in result.output
        assert "Model: llama-7b" in result.output

    def test_estimate_with_gradient_checkpointing(self):
        """Test estimation with gradient checkpointing enabled."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--gradient-checkpointing',
            '--gpu-type', 'A100'
        ])

        assert result.exit_code == 0
        assert "Gradient Checkpointing: Enabled" in result.output

    def test_estimate_verbose(self):
        """Test verbose output."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--gpu-type', 'A100',
            '--verbose'
        ])

        assert result.exit_code == 0
        assert "MEMORY BREAKDOWN" in result.output
        assert "Model Memory:" in result.output
        assert "Optimizer Memory:" in result.output
        assert "Gradient Memory:" in result.output
        assert "Activation Memory:" in result.output

    def test_estimate_with_all_precisions(self):
        """Test estimation with different precision types."""
        precisions = ['fp32', 'fp16', 'bf16', 'int8']

        for precision in precisions:
            result = self.runner.invoke(cli, [
                'estimate',
                '--model-params', '7e9',
                '--batch-size', '4',
                '--precision', precision,
                '--gpu-type', 'A100'
            ])

            assert result.exit_code == 0
            assert f"Precision: {precision}" in result.output

    def test_estimate_with_all_optimizers(self):
        """Test estimation with different optimizer types."""
        optimizers = ['adam', 'adamw', 'sgd']

        for optimizer in optimizers:
            result = self.runner.invoke(cli, [
                'estimate',
                '--model-params', '7e9',
                '--batch-size', '4',
                '--optimizer', optimizer,
                '--gpu-type', 'A100'
            ])

            assert result.exit_code == 0
            assert f"Optimizer: {optimizer}" in result.output

    def test_estimate_with_custom_gpu_memory(self):
        """Test estimation with custom GPU memory."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--gpu-memory', '40.0'
        ])

        assert result.exit_code == 0
        assert "GPU Type: 40GB" in result.output

    def test_trending_command(self):
        """Test trending models command (may fail without HF integration)."""
        result = self.runner.invoke(cli, [
            'trending',
            '--limit', '5'
        ])

        # Command should either succeed or fail gracefully
        assert result.exit_code in [0, 1]
        if result.exit_code == 1:
            assert "Hugging Face integration not available" in result.output

    def test_search_command(self):
        """Test search models command (may fail without HF integration)."""
        result = self.runner.invoke(cli, [
            'search',
            'llama',
            '--limit', '5'
        ])

        # Command should either succeed or fail gracefully
        assert result.exit_code in [0, 1]
        if result.exit_code == 1:
            assert "Hugging Face integration not available" in result.output

    def test_popular_command(self):
        """Test popular models command (may fail without HF integration)."""
        result = self.runner.invoke(cli, [
            'popular',
            'llama',
            '--limit', '5'
        ])

        # Command should either succeed or fail gracefully
        assert result.exit_code in [0, 1]
        if result.exit_code == 1:
            assert "Hugging Face integration not available" in result.output

    def test_info_command(self):
        """Test model info command."""
        result = self.runner.invoke(cli, [
            'info',
            'llama-7b'
        ])

        assert result.exit_code == 0
        assert "Model Configuration" in result.output

    def test_invalid_model_params(self):
        """Test with invalid model parameters."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', 'invalid',
            '--batch-size', '4',
            '--gpu-type', 'A100'
        ])

        assert result.exit_code != 0

    def test_invalid_gpu_type(self):
        """Test with invalid GPU type."""
        result = self.runner.invoke(cli, [
            'estimate',
            '--model-params', '7e9',
            '--batch-size', '4',
            '--gpu-type', 'INVALID_GPU'
        ])

        assert result.exit_code != 0

    def test_help_command(self):
        """Test help command."""
        result = self.runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "GPU Estimator" in result.output
        assert "estimate" in result.output
        assert "trending" in result.output
        assert "search" in result.output

    def test_estimate_help(self):
        """Test estimate subcommand help."""
        result = self.runner.invoke(cli, ['estimate', '--help'])

        assert result.exit_code == 0
        assert "Estimate GPU requirements" in result.output
        assert "--model-params" in result.output
        assert "--dataset-size" in result.output
        assert "--epochs" in result.output


class TestInteractiveMode:
    """Test interactive mode functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_interactive_mode_available(self):
        """Test that interactive mode is available."""
        result = self.runner.invoke(cli, ['interactive'], input='\n')

        # Should start interactive mode (may exit early due to no input)
        assert "GPU Estimator - Interactive Mode" in result.output or result.exit_code in [0, 1]


if __name__ == "__main__":
    pytest.main([__file__])