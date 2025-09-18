import os
import datetime
from torch.utils.tensorboard import SummaryWriter
from distinanet.utils import setup_logger
import torch

def setup_training_logging(args, logger_name: str = "training"):
    """
    Sets up the main logger and TensorBoard writer.
    
    Args:
        args: Training arguments
        logger_name: Name for the logger (default: "training")
    """
    logger = setup_logger(logger_name, "INFO")
    logger.info(f'CUDA available: {torch.cuda.is_available()}')
    logger.info(f'Device: {args.device}')
    logger.info(f'Current cuda device: {torch.cuda.current_device()}')
    logger.info(f'Count of using GPUs: {torch.cuda.device_count()}')
    logger.info(f"Using seed number: {args.seed}")
    logger.info(f"Learning rate: {args.lr}")
    logger.info(f"Distance Loss Weight: {args.distance_weight}")

    if args.load_checkpoint:
        timestamp = args.load_checkpoint.split('/')[-3]
        log_dir = f"runs/{timestamp}"
    else:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = f"runs/{timestamp}"
        
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    writer = SummaryWriter(log_dir=log_dir)
    logger.info(f"Logdir for tensorboard: {log_dir}")
    
    return logger, writer, log_dir
