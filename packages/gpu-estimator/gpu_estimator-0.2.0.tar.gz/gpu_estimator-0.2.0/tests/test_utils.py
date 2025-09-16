"""
Tests for utility functions.
"""
import pytest
from gpu_estimator.utils import (
    get_model_config,
    calculate_transformer_params,
    format_number
)


class TestUtils:
    """Test utility functions."""

    def test_get_model_config(self):
        """Test getting model configurations."""
        # Test known model
        config = get_model_config("llama-7b")
        assert isinstance(config, dict)
        assert "num_layers" in config
        assert "hidden_size" in config
        assert "num_attention_heads" in config
        assert "vocab_size" in config

        # Test all supported models
        supported_models = [
            "gpt2", "llama-7b", "llama-13b", "llama-30b",
            "llama2-7b", "mistral-7b", "phi-1.5b", "gemma-7b"
        ]

        for model_name in supported_models:
            config = get_model_config(model_name)
            assert isinstance(config, dict)
            assert all(key in config for key in [
                "num_layers", "hidden_size", "num_attention_heads", "vocab_size"
            ])

    def test_get_model_config_unknown(self):
        """Test getting config for unknown model."""
        with pytest.raises(ValueError, match="Unknown model"):
            get_model_config("unknown-model")

    def test_calculate_transformer_params(self):
        """Test transformer parameter calculation."""
        # Test with known values
        params = calculate_transformer_params(
            num_layers=32,
            hidden_size=4096,
            num_attention_heads=32,
            vocab_size=32000
        )

        assert isinstance(params, (int, float))
        assert params > 0

        # Larger models should have more parameters
        small_params = calculate_transformer_params(
            num_layers=12,
            hidden_size=768,
            num_attention_heads=12,
            vocab_size=50257
        )

        large_params = calculate_transformer_params(
            num_layers=32,
            hidden_size=4096,
            num_attention_heads=32,
            vocab_size=32000
        )

        assert large_params > small_params

    def test_calculate_transformer_params_validation(self):
        """Test parameter validation in transformer calculation."""
        # Test with zero values
        with pytest.raises((ValueError, ZeroDivisionError)):
            calculate_transformer_params(0, 4096, 32, 32000)

        with pytest.raises((ValueError, ZeroDivisionError)):
            calculate_transformer_params(32, 0, 32, 32000)

        # Test with negative values
        with pytest.raises(ValueError):
            calculate_transformer_params(-1, 4096, 32, 32000)

    def test_format_number(self):
        """Test number formatting function."""
        # Test billions
        assert format_number(7e9) == "7.0B"
        assert format_number(13.5e9) == "13.5B"

        # Test millions
        assert format_number(175e6) == "175.0M"
        assert format_number(1.5e6) == "1.5M"

        # Test thousands
        assert format_number(175e3) == "175.0K"
        assert format_number(1.5e3) == "1.5K"

        # Test small numbers
        assert format_number(999) == "999"
        assert format_number(100) == "100"

        # Test zero
        assert format_number(0) == "0"

        # Test very large numbers
        assert format_number(1e12) == "1000.0B"

    def test_format_number_edge_cases(self):
        """Test edge cases for number formatting."""
        # Test with decimals that should round
        assert format_number(7.123e9) == "7.1B"
        assert format_number(7.156e9) == "7.2B"

        # Test boundary cases
        assert format_number(999999) == "1000.0K"
        assert format_number(999999999) == "1000.0M"

    def test_model_config_consistency(self):
        """Test that model configs are consistent."""
        # Test that all models have reasonable parameter counts
        models_to_test = [
            ("gpt2", 117e6),  # ~117M parameters
            ("llama-7b", 6.7e9),  # ~6.7B parameters
            ("llama-13b", 13e9),  # ~13B parameters
        ]

        for model_name, expected_approx in models_to_test:
            config = get_model_config(model_name)
            calculated_params = calculate_transformer_params(**config)

            # Allow for some variance in parameter calculation
            ratio = calculated_params / expected_approx
            assert 0.8 <= ratio <= 1.2, f"Parameter count for {model_name} seems off: {calculated_params} vs expected ~{expected_approx}"


class TestModelConfigs:
    """Test specific model configurations."""

    def test_gpt2_config(self):
        """Test GPT-2 configuration."""
        config = get_model_config("gpt2")

        assert config["num_layers"] == 12
        assert config["hidden_size"] == 768
        assert config["num_attention_heads"] == 12
        assert config["vocab_size"] == 50257

    def test_llama_configs(self):
        """Test LLaMA model configurations."""
        llama_7b = get_model_config("llama-7b")
        llama_13b = get_model_config("llama-13b")
        llama_30b = get_model_config("llama-30b")

        # 13B should have more layers than 7B
        assert llama_13b["num_layers"] > llama_7b["num_layers"]

        # 30B should have more layers than 13B
        assert llama_30b["num_layers"] > llama_13b["num_layers"]

        # All should have same vocab size
        assert llama_7b["vocab_size"] == llama_13b["vocab_size"] == llama_30b["vocab_size"]

    def test_all_models_have_valid_params(self):
        """Test that all model configurations result in valid parameter counts."""
        supported_models = [
            "gpt2", "llama-7b", "llama-13b", "llama-30b",
            "llama2-7b", "mistral-7b", "phi-1.5b", "gemma-7b"
        ]

        for model_name in supported_models:
            config = get_model_config(model_name)
            params = calculate_transformer_params(**config)

            # Should be a reasonable number of parameters
            assert 1e6 <= params <= 100e9, f"Parameter count for {model_name} seems unreasonable: {params}"


if __name__ == "__main__":
    pytest.main([__file__])