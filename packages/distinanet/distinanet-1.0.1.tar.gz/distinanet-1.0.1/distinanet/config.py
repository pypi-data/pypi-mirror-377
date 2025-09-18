import argparse
import torch
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for DistinaNet training and evaluation"""
    
    # Data paths
    csv_train: str = 'kitti_dataset/annotations/train.csv'
    csv_classes: str = 'kitti_dataset/classes.csv'
    csv_val: str = 'kitti_dataset/annotations/validation.csv'
    
    # Model configuration
    depth: int = 18
    distance_head_type: str = 'base'
    distance_loss_type: str = 'huber'
    distance_weight: float = 1.0
    
    # Training configuration
    num_gpus: int = 1
    batch_size: int = 2
    epochs: int = 10
    lr: float = 1e-4
    optimizer: str = "adam"
    load_checkpoint: Optional[str] = None
    
    # System configuration
    seed: int = 16
    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def validate(self):
        """Validate configuration parameters"""
        # Validate depth
        valid_depths = [18, 34, 50, 101, 152]
        if self.depth not in valid_depths:
            raise ValueError(f"Resnet depth must be one of: {valid_depths}, got {self.depth}")
        
        # Validate distance head type
        valid_heads = ['base', 'deep', 'bottleneck', 'cbam', 'dynamicbranching']
        if self.distance_head_type not in valid_heads:
            raise ValueError(f"Distance head type must be one of: {valid_heads}, got {self.distance_head_type}")
        
        # Validate distance loss type
        valid_losses = ['huber', 'l1', 'l2', 'smoothl1', 'logcosh']
        if self.distance_loss_type not in valid_losses:
            raise ValueError(f"Distance loss type must be one of: {valid_losses}, got {self.distance_loss_type}")
        
        # Validate other parameters
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        if self.epochs <= 0:
            raise ValueError("Number of epochs must be positive")
        if self.lr <= 0:
            raise ValueError("Learning rate must be positive")

class ConfigParser:
    """Handles command-line argument parsing"""
    
    @staticmethod
    def create_parser():
        """Create argument parser with all training options"""
        parser = argparse.ArgumentParser(
            description='Simple training script for training a Distinanet network.'
        )
        
        # Data arguments
        data_group = parser.add_argument_group('Data Configuration')
        data_group.add_argument('--csv_train', 
                               help='Path to file containing training annotations (see readme)', 
                               default='kitti_dataset/annotations/train.csv')
        data_group.add_argument('--csv_classes', 
                               help='Path to file containing class list (see readme)', 
                               default='kitti_dataset/classes.csv')
        data_group.add_argument('--csv_val', 
                               help='Path to file containing validation annotations (optional, see readme)', 
                               default='kitti_dataset/annotations/validation.csv')
        
        # Model arguments
        model_group = parser.add_argument_group('Model Configuration')
        model_group.add_argument('--depth', 
                                help='Resnet depth, must be one of: 18, 34, 50, 101, 152', 
                                type=int, default=18,
                                choices=[18, 34, 50, 101, 152])
        model_group.add_argument('--distance_head_type', 
                                help='Distance Head type must be one of: base, deep, bottleneck, cbam, dynamicbranching',
                                type=str, default='base',
                                choices=['base', 'deep', 'bottleneck', 'cbam', 'dynamicbranching'])
        model_group.add_argument('--distance_loss_type', 
                                help='Loss Function, must be one of: huber, l1, l2, smoothl1, logcosh',
                                type=str, default='huber',
                                choices=['huber', 'l1', 'l2', 'smoothl1', 'logcosh'])
        model_group.add_argument('--distance_weight', 
                                help='Weight for distance loss', 
                                type=float, default=1.0)
        
        # Training arguments
        train_group = parser.add_argument_group('Training Configuration')
        train_group.add_argument('--num_gpus', 
                                help='Number of GPUs to use for training', 
                                type=int, default=1)
        train_group.add_argument('--batch_size', 
                                help='Batch size', 
                                type=int, default=2)
        train_group.add_argument('--epochs', 
                                help='Number of epochs', 
                                type=int, default=10)
        train_group.add_argument('--lr', 
                                help='Learning rate', 
                                type=float, default=1e-4)
        train_group.add_argument('--optimizer', 
                                help='Optimizer type', 
                                type=str, default="adam")
        train_group.add_argument('--load_checkpoint', 
                                help='Path to a .pt file to load checkpoint', 
                                type=str)
        
        return parser
    
    @staticmethod
    def parse_args():
        """Parse command line arguments and return Config object"""
        parser = ConfigParser.create_parser()
        args = parser.parse_args()
        
        # Create config from parsed arguments
        config = Config(
            csv_train=args.csv_train,
            csv_classes=args.csv_classes,
            csv_val=args.csv_val,
            depth=args.depth,
            distance_head_type=args.distance_head_type,
            distance_loss_type=args.distance_loss_type,
            distance_weight=args.distance_weight,
            num_gpus=args.num_gpus,
            batch_size=args.batch_size,
            epochs=args.epochs,
            lr=args.lr,
            optimizer=args.optimizer,
            load_checkpoint=args.load_checkpoint
        )
        
        # Validate configuration
        config.validate()
        
        return config
