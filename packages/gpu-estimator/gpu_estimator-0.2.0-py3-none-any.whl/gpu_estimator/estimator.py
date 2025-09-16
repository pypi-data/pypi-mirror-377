from dataclasses import dataclass
from typing import Optional, Dict, Any
import math
import warnings

try:
    from .huggingface_models import HuggingFaceModelRegistry
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


@dataclass
class EstimationResult:
    """Result of GPU estimation calculation."""
    memory_per_gpu_gb: float
    num_gpus: int
    total_memory_gb: float
    model_memory_gb: float
    optimizer_memory_gb: float
    activation_memory_gb: float
    gradient_memory_gb: float
    efficiency_ratio: float
    estimated_training_hours: Optional[float] = None
    total_steps: Optional[int] = None
    steps_per_epoch: Optional[int] = None
    estimated_cost_usd: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_per_gpu_gb": self.memory_per_gpu_gb,
            "num_gpus": self.num_gpus,
            "total_memory_gb": self.total_memory_gb,
            "model_memory_gb": self.model_memory_gb,
            "optimizer_memory_gb": self.optimizer_memory_gb,
            "activation_memory_gb": self.activation_memory_gb,
            "gradient_memory_gb": self.gradient_memory_gb,
            "efficiency_ratio": self.efficiency_ratio,
            "estimated_training_hours": self.estimated_training_hours,
            "total_steps": self.total_steps,
            "steps_per_epoch": self.steps_per_epoch,
            "estimated_cost_usd": self.estimated_cost_usd
        }


class GPUEstimator:
    """Estimates GPU memory requirements and optimal GPU count for training."""
    
    def __init__(self):
        self.precision_bytes = {
            "fp32": 4,
            "fp16": 2,
            "bf16": 2,
            "int8": 1
        }
        
        # Common GPU memory sizes in GB
        self.gpu_memory_sizes = {
            "V100": 32,
            "A100": 80,
            "H100": 80,
            "B200": 192,
            "RTX3090": 24,
            "RTX4090": 24,
            "T4": 16,
            "L4": 24,
            "L40": 48,
            "A40": 48,
            "A6000": 48
        }
        
        # Initialize Hugging Face registry if available
        self.hf_registry = None
        if HF_AVAILABLE:
            try:
                self.hf_registry = HuggingFaceModelRegistry()
            except ImportError:
                warnings.warn("Hugging Face integration not available", UserWarning)

        # GPU hourly rates (rough estimates in USD)
        self.gpu_hourly_rates = {
            "V100": 2.48,    # AWS p3.2xlarge
            "A100": 4.10,    # AWS p4d.large
            "H100": 8.00,    # Estimated cloud pricing
            "B200": 15.00,   # Estimated next-gen pricing
            "RTX3090": 0.50, # Consumer GPU estimate
            "RTX4090": 0.80, # Consumer GPU estimate
            "T4": 0.53,      # AWS g4dn.xlarge
            "L4": 1.20,      # Estimated
            "L40": 2.00,     # Estimated
            "A40": 2.50,     # AWS g5.xlarge
            "A6000": 2.80    # Workstation estimate
        }
    
    def estimate(
        self,
        model_params: float,
        batch_size: int = 1,
        sequence_length: int = 2048,
        precision: str = "fp16",
        optimizer: str = "adam",
        gpu_memory_gb: Optional[float] = None,
        gpu_type: Optional[str] = None,
        gradient_checkpointing: bool = False,
        parallelism_efficiency: float = 0.85,
        dataset_size: Optional[int] = None,
        epochs: int = 3,
        steps_per_second_per_gpu: Optional[float] = None
    ) -> EstimationResult:
        """
        Estimate GPU requirements for training.

        Args:
            model_params: Number of model parameters
            batch_size: Training batch size
            sequence_length: Input sequence length
            precision: Model precision (fp32, fp16, bf16)
            optimizer: Optimizer type (adam, sgd, adamw)
            gpu_memory_gb: Available GPU memory in GB
            gpu_type: GPU type (V100, A100, H100, etc.)
            gradient_checkpointing: Whether gradient checkpointing is enabled
            parallelism_efficiency: Efficiency of parallelism (0.0-1.0)
            dataset_size: Number of samples in dataset
            epochs: Number of training epochs
            steps_per_second_per_gpu: Training throughput (auto-estimated if None)

        Returns:
            EstimationResult with memory breakdown, GPU count, and training time
        """
        if gpu_type and gpu_type in self.gpu_memory_sizes:
            gpu_memory_gb = self.gpu_memory_sizes[gpu_type]
        elif gpu_memory_gb is None:
            gpu_memory_gb = 80  # Default to A100
        
        bytes_per_param = self.precision_bytes.get(precision, 2)
        
        # Model memory (parameters)
        model_memory_gb = (model_params * bytes_per_param) / (1024**3)
        
        # Optimizer state memory
        optimizer_multiplier = self._get_optimizer_multiplier(optimizer, precision)
        optimizer_memory_gb = model_memory_gb * optimizer_multiplier
        
        # Gradient memory
        gradient_memory_gb = model_memory_gb
        
        # Activation memory (rough estimate)
        activation_memory_gb = self._estimate_activation_memory(
            batch_size, sequence_length, model_params, bytes_per_param, 
            gradient_checkpointing
        )
        
        # Total memory required
        total_memory_gb = (
            model_memory_gb + 
            optimizer_memory_gb + 
            gradient_memory_gb + 
            activation_memory_gb
        )
        
        # Add 20% overhead for framework and other memory usage
        total_memory_gb *= 1.2
        
        # Calculate number of GPUs needed
        memory_per_gpu = gpu_memory_gb * 0.9  # Leave 10% buffer
        min_gpus = max(1, math.ceil(total_memory_gb / memory_per_gpu))
        
        # Adjust for parallelism efficiency
        actual_memory_per_gpu = total_memory_gb / min_gpus if min_gpus > 0 else 0
        efficiency_ratio = min(1.0, parallelism_efficiency)

        # Calculate training time estimates
        estimated_training_hours = None
        total_steps = None
        steps_per_epoch = None
        estimated_cost_usd = None

        if dataset_size is not None:
            steps_per_epoch = math.ceil(dataset_size / batch_size)
            total_steps = steps_per_epoch * epochs

            # Estimate throughput if not provided
            if steps_per_second_per_gpu is None:
                steps_per_second_per_gpu = self._estimate_throughput(
                    model_params, batch_size, sequence_length, gpu_type or "A100"
                )

            # Calculate training time considering parallelism
            effective_throughput = steps_per_second_per_gpu * min_gpus * efficiency_ratio
            training_seconds = total_steps / effective_throughput if effective_throughput > 0 else 0
            estimated_training_hours = training_seconds / 3600

            # Calculate cost estimate
            if gpu_type and gpu_type in self.gpu_hourly_rates:
                hourly_rate = self.gpu_hourly_rates[gpu_type]
                estimated_cost_usd = estimated_training_hours * min_gpus * hourly_rate

        return EstimationResult(
            memory_per_gpu_gb=actual_memory_per_gpu,
            num_gpus=min_gpus,
            total_memory_gb=total_memory_gb,
            model_memory_gb=model_memory_gb,
            optimizer_memory_gb=optimizer_memory_gb,
            activation_memory_gb=activation_memory_gb,
            gradient_memory_gb=gradient_memory_gb,
            efficiency_ratio=efficiency_ratio,
            estimated_training_hours=estimated_training_hours,
            total_steps=total_steps,
            steps_per_epoch=steps_per_epoch,
            estimated_cost_usd=estimated_cost_usd
        )
    
    def _get_optimizer_multiplier(self, optimizer: str, precision: str) -> float:
        """Get memory multiplier for optimizer states."""
        if optimizer.lower() in ["adam", "adamw"]:
            # Adam stores momentum and variance (2x parameters)
            if precision == "fp32":
                return 2.0
            else:
                # Mixed precision: optimizer states in fp32
                return 4.0
        elif optimizer.lower() == "sgd":
            # SGD with momentum (1x parameters)
            if precision == "fp32":
                return 1.0
            else:
                return 2.0
        else:
            # Default to Adam-like
            return 2.0 if precision == "fp32" else 4.0
    
    def _estimate_activation_memory(
        self, 
        batch_size: int, 
        sequence_length: int, 
        model_params: float,
        bytes_per_param: int,
        gradient_checkpointing: bool
    ) -> float:
        """Rough estimate of activation memory."""
        # Very rough heuristic: activations scale with batch_size * seq_len * sqrt(params)
        activation_scale = batch_size * sequence_length * math.sqrt(model_params)
        activation_memory_gb = (activation_scale * bytes_per_param) / (1024**3)
        
        # Apply gradient checkpointing reduction
        if gradient_checkpointing:
            activation_memory_gb *= 0.3  # Roughly 70% reduction
        
        return activation_memory_gb

    def _estimate_throughput(
        self,
        model_params: float,
        batch_size: int,
        sequence_length: int,
        gpu_type: str
    ) -> float:
        """
        Estimate training throughput in steps per second per GPU.

        This is a rough heuristic based on model size and GPU capabilities.
        """
        # Base throughput estimates (steps/sec/GPU) for different model sizes
        # These are rough estimates based on common training scenarios
        if model_params < 1e9:  # < 1B parameters
            base_throughput = 10.0
        elif model_params < 7e9:  # 1B-7B parameters
            base_throughput = 2.0
        elif model_params < 15e9:  # 7B-15B parameters
            base_throughput = 0.8
        elif model_params < 70e9:  # 15B-70B parameters
            base_throughput = 0.3
        else:  # > 70B parameters
            base_throughput = 0.1

        # Adjust for batch size (smaller batches = lower efficiency)
        batch_factor = min(1.0, batch_size / 8.0)

        # Adjust for sequence length (longer sequences = slower)
        seq_factor = min(1.0, 2048.0 / sequence_length)

        # Adjust for GPU type
        gpu_factors = {
            "V100": 0.6,
            "A100": 1.0,
            "H100": 1.8,
            "B200": 2.5,
            "RTX3090": 0.4,
            "RTX4090": 0.7,
            "T4": 0.3,
            "L4": 0.5,
            "L40": 0.8,
            "A40": 0.7,
            "A6000": 0.6
        }
        gpu_factor = gpu_factors.get(gpu_type, 1.0)

        return base_throughput * batch_factor * seq_factor * gpu_factor

    def estimate_cost(
        self,
        result: EstimationResult,
        gpu_type: Optional[str] = None,
        hourly_rate: Optional[float] = None
    ) -> float:
        """
        Estimate training cost in USD.

        Args:
            result: EstimationResult from estimate()
            gpu_type: GPU type for rate lookup
            hourly_rate: Custom hourly rate per GPU (overrides gpu_type lookup)

        Returns:
            Estimated cost in USD
        """
        if result.estimated_training_hours is None:
            raise ValueError("Training time not calculated. Provide dataset_size to estimate() method.")

        if hourly_rate is not None:
            rate = hourly_rate
        elif gpu_type and gpu_type in self.gpu_hourly_rates:
            rate = self.gpu_hourly_rates[gpu_type]
        else:
            rate = self.gpu_hourly_rates["A100"]  # Default rate

        return result.estimated_training_hours * result.num_gpus * rate

    def estimate_from_architecture(
        self,
        num_layers: int,
        hidden_size: int,
        num_attention_heads: int,
        vocab_size: int,
        **kwargs
    ) -> EstimationResult:
        """Estimate based on transformer architecture parameters."""
        from .utils import calculate_transformer_params
        
        model_params = calculate_transformer_params(
            num_layers, hidden_size, num_attention_heads, vocab_size
        )
        
        return self.estimate(model_params=model_params, **kwargs)
    
    def estimate_from_huggingface(
        self,
        model_id: str,
        **kwargs
    ) -> EstimationResult:
        """
        Estimate GPU requirements for a Hugging Face model.
        
        Args:
            model_id: Hugging Face model ID (e.g., "meta-llama/Llama-2-7b-hf")
            **kwargs: Additional arguments passed to estimate()
        
        Returns:
            EstimationResult with memory breakdown and GPU count
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        # Get model parameters from Hugging Face
        model_params = self.hf_registry.estimate_model_parameters(model_id)
        if model_params is None:
            raise ValueError(f"Could not determine parameters for model: {model_id}")
        
        return self.estimate(model_params=model_params, **kwargs)
    
    def list_trending_models(self, limit: int = 20, task: Optional[str] = None):
        """
        List trending models from Hugging Face.
        
        Args:
            limit: Maximum number of models to return
            task: Filter by task (e.g., "text-generation")
        
        Returns:
            List of model information
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.list_trending_models(limit=limit, task=task)
    
    def search_models(self, query: str, limit: int = 20, task: Optional[str] = None):
        """
        Search for models on Hugging Face.
        
        Args:
            query: Search query
            limit: Maximum number of models to return
            task: Filter by task
        
        Returns:
            List of model information
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.search_models(query=query, limit=limit, task=task)
    
    def get_popular_models_by_architecture(self, architecture: str, limit: int = 10):
        """
        Get popular models for a specific architecture.
        
        Args:
            architecture: Architecture name (e.g., "llama", "gpt", "bert")
            limit: Maximum number of models to return
        
        Returns:
            List of popular models for the architecture
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.get_popular_models_by_architecture(architecture=architecture, limit=limit)