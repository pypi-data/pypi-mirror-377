"""Simple trainer class to organize training logic"""

import torch
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import os
from typing import Optional
from .common import create_run_directory

class Trainer:
    """Handles model training logic and utilities"""
    
    def __init__(self, config, run_dir: Optional[str] = None):
        self.config = config
        self.run_dir = run_dir or create_run_directory()
        self.writer: Optional[SummaryWriter] = None
        self.setup_environment()
    
    def setup_environment(self):
        """Setup training environment with run directory structure"""
        # Set random seeds
        torch.manual_seed(self.config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.seed)
        
        # Setup tensorboard with run directory
        logs_dir = os.path.join(self.run_dir, 'logs')
        self.writer = SummaryWriter(logs_dir)
        print(f"Training environment setup complete. Device: {self.config.device}")
        print(f"📊 TensorBoard logs: {logs_dir}")
    
    @property
    def checkpoints_dir(self):
        """Get the checkpoints directory for this run"""
        return os.path.join(self.run_dir, 'checkpoints')
    
    @property
    def test_dir(self):
        """Get the test directory for this run"""
        return os.path.join(self.run_dir, 'test')
    
    def create_optimizer(self, model):
        """Create optimizer based on config"""
        if self.config.optimizer.lower() == 'adam':
            return optim.Adam(model.parameters(), lr=self.config.lr)
        elif self.config.optimizer.lower() == 'sgd':
            return optim.SGD(model.parameters(), lr=self.config.lr, momentum=0.9)
        else:
            raise ValueError(f"Unknown optimizer: {self.config.optimizer}")
    
    def save_checkpoint(self, model, optimizer, epoch, loss):
        """Save training checkpoint"""
        checkpoint_path = os.path.join(self.checkpoints_dir, f'epoch_{epoch}.pt')
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
            'config_dict': {
                'depth': self.config.depth,
                'distance_head_type': self.config.distance_head_type,
                'distance_loss_type': self.config.distance_loss_type,
                'distance_weight': self.config.distance_weight
            }
        }, checkpoint_path)
        print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, model, optimizer):
        """Load checkpoint if specified"""
        if not self.config.load_checkpoint:
            return 0
        
        if not os.path.exists(self.config.load_checkpoint):
            print(f"Checkpoint not found: {self.config.load_checkpoint}")
            return 0
        
        checkpoint = torch.load(self.config.load_checkpoint, map_location=self.config.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        if optimizer:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        print(f"Checkpoint loaded: {self.config.load_checkpoint}")
        return checkpoint['epoch']
    
    def log_metrics(self, epoch, train_loss, val_map=None, val_mae=None):
        """Log metrics to tensorboard"""
        if self.writer:
            self.writer.add_scalar('Loss/Train', train_loss, epoch)
            if val_map is not None:
                self.writer.add_scalar('mAP/Validation', val_map, epoch)
            if val_mae is not None:
                self.writer.add_scalar('MAE/Validation', val_mae, epoch)
    
    def print_training_info(self):
        """Print training configuration info"""
        print("\n" + "="*50)
        print("TRAINING CONFIGURATION")
        print("="*50)
        print(f"Model depth: {self.config.depth}")
        print(f"Distance head: {self.config.distance_head_type}")
        print(f"Distance loss: {self.config.distance_loss_type}")
        print(f"Epochs: {self.config.epochs}")
        print(f"Batch size: {self.config.batch_size}")
        print(f"Learning rate: {self.config.lr}")
        print(f"Optimizer: {self.config.optimizer}")
        print(f"Device: {self.config.device}")
        print("="*50 + "\n")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.writer:
            self.writer.close()
