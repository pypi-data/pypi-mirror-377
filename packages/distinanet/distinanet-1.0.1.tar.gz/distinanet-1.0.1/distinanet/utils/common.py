"""Common utility functions for DistinaNet"""

import os
import torch
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

def create_run_directory() -> str:
    """
    Create a timestamped run directory for organizing training outputs.
    
    Returns:
        str: Path to the created run directory
    """
    # Create timestamp in format: YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = f"runs/{timestamp}"
    
    # Create the run directory and subdirectories
    subdirs = ['logs', 'checkpoints', 'test']
    for subdir in subdirs:
        os.makedirs(os.path.join(run_dir, subdir), exist_ok=True)
    
    print(f"📁 Created run directory: {run_dir}")
    print(f"   ├─ logs/         (TensorBoard logs)")
    print(f"   ├─ checkpoints/  (Model checkpoints)")
    print(f"   └─ test/         (Test results)")
    
    return run_dir

def setup_directories():
    """Create necessary directories for training/evaluation (legacy support)"""
    dirs = ['logs', 'checkpoints', 'results', 'outputs']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("Directories setup complete.")

def set_random_seeds(seed: int = 16):
    """Set random seeds for reproducibility"""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    print(f"Random seeds set to {seed}")

def get_device(force_cpu: bool = False) -> torch.device:
    """Get the appropriate device for computation"""
    if force_cpu:
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Using device: {device}")
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    return device

def print_model_summary(model, input_size=(3, 512, 512)):
    """Print a summary of the model architecture"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print("\n" + "="*60)
    print("MODEL SUMMARY")
    print("="*60)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Non-trainable parameters: {total_params - trainable_params:,}")
    print("="*60 + "\n")

def format_time(seconds: float) -> str:
    """Format time in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

def save_experiment_config(config, save_path: str):
    """Save experiment configuration to file"""
    import json
    
    # Convert config object to dictionary
    if hasattr(config, '__dict__'):
        config_dict = config.__dict__.copy()
    else:
        config_dict = vars(config).copy()
    
    # Handle non-serializable objects
    for key, value in config_dict.items():
        if isinstance(value, torch.device):
            config_dict[key] = str(value)
        elif hasattr(value, '__dict__'):
            config_dict[key] = str(value)
    
    with open(save_path, 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    print(f"Configuration saved to: {save_path}")

def calculate_metrics_summary(predictions: list, ground_truth: list) -> Dict[str, float]:
    """Calculate a summary of evaluation metrics"""
    # This is a placeholder that can be expanded based on your specific metrics
    metrics = {
        'total_predictions': len(predictions),
        'total_ground_truth': len(ground_truth),
    }
    
    return metrics

class ProgressTracker:
    """Simple progress tracking for training/evaluation"""
    
    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.description = description
        self.start_time = None
    
    def start(self):
        """Start tracking progress"""
        import time
        self.start_time = time.time()
        self.update(0)
    
    def update(self, current: int):
        """Update progress"""
        import time
        self.current_item = current
        
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            if current > 0:
                eta = elapsed * (self.total_items - current) / current
                eta_str = format_time(eta)
                elapsed_str = format_time(elapsed)
                print(f"\r{self.description}: {current}/{self.total_items} "
                      f"({100*current/self.total_items:.1f}%) "
                      f"[Elapsed: {elapsed_str}, ETA: {eta_str}]", end="")
            else:
                print(f"\r{self.description}: {current}/{self.total_items} (0.0%)", end="")
    
    def finish(self):
        """Finish progress tracking"""
        import time
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            elapsed_str = format_time(elapsed)
            print(f"\r{self.description}: {self.total_items}/{self.total_items} "
                  f"(100.0%) [Total time: {elapsed_str}]")
        else:
            print(f"\r{self.description}: Complete!")
        print()  # New line
