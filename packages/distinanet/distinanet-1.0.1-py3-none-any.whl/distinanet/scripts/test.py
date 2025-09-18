import os
import argparse
import torch
import torch.multiprocessing as mp
from torchvision import transforms
from tqdm import tqdm

from distinanet.data.datasets import CSVDataset
from distinanet.data.transforms import Resizer, Normalizer
from distinanet.utils import ModelEvaluator, setup_logger, get_device

assert torch.__version__.split('.')[0] == '1'

# Set multiprocessing start method for CUDA compatibility
try:
    mp.set_start_method('spawn', force=True)
except RuntimeError:
    pass

logger = setup_logger("testing", "INFO")

def main(args=None):
    parser = argparse.ArgumentParser(description='Evaluate a trained DistinaNet model.')

    parser.add_argument('--csv_annotations_path', help='Path to CSV annotations', required=True)
    parser.add_argument('--model_path', help='Path to model', type=str, required=True)
    parser.add_argument('--images_path', help='Path to images directory', type=str)
    parser.add_argument('--class_list_path', help='Path to classlist csv', type=str, required=True)
    parser.add_argument('--iou_threshold', help='IOU threshold used for evaluation', type=float, default=0.5)
    parser.add_argument('--save_path', help='Save path for plots', type=str, default=None)
    parser.add_argument('--run_dir', help='Run directory for organized results (auto-detects from model path if not specified)', type=str, default=None)
    parser = parser.parse_args(args)

    # Auto-detect run directory from model path if not specified
    if parser.run_dir is None and parser.save_path is None:
        # Try to extract run directory from model path
        model_path_parts = parser.model_path.split(os.sep)
        if 'runs' in model_path_parts:
            runs_idx = model_path_parts.index('runs')
            if runs_idx + 1 < len(model_path_parts):
                parser.run_dir = os.path.join(*model_path_parts[:runs_idx+2])
                parser.save_path = os.path.join(parser.run_dir, 'test')
                logger.info(f"Auto-detected run directory: {parser.run_dir}")
                logger.info(f"Test results will be saved to: {parser.save_path}")
        
        # Create test directory if it doesn't exist
        if parser.save_path and not os.path.exists(parser.save_path):
            os.makedirs(parser.save_path, exist_ok=True)
            logger.info(f"Created test results directory: {parser.save_path}")

    # Get device
    device = get_device()
    logger.info('CUDA available: {}'.format(torch.cuda.is_available()))

    # Setup dataset
    dataset_val = CSVDataset(
        parser.csv_annotations_path, 
        parser.class_list_path,
        transform=transforms.Compose([Normalizer(), Resizer()]),
        device='cpu'  # Keep dataset on CPU to avoid CUDA multiprocessing issues
    )
    logger.info("Length of test Dataset: %d", len(dataset_val))

    # Load model
    logger.info(f"Loading model from: {parser.model_path}")
    
    # Check if loading from checkpoint or complete model file
    checkpoint = torch.load(parser.model_path, map_location=device)
    
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        # Loading from checkpoint - need to reconstruct model
        logger.info("Loading from checkpoint file...")
        
        # Extract model configuration from checkpoint
        config_dict = checkpoint.get('config_dict', {})
        num_classes = dataset_val.num_classes()
        
        # Import and create model
        from distinanet.model.model import DistinaNet
        distinanet = DistinaNet(
            num_classes=num_classes,
            backbone_depth=config_dict.get('depth', 18),
            pretrained=False,  # Don't load pretrained weights when loading from checkpoint
            distance_head_type=config_dict.get('distance_head_type', 'base'),
            distance_loss_type=config_dict.get('distance_loss_type', 'huber')
        )
        
        # Load the saved state dict
        distinanet.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
        
    else:
        # Loading complete model file (legacy)
        logger.info("Loading complete model file...")
        distinanet = checkpoint

    # Move model to device and set to evaluation mode
    distinanet = distinanet.to(device)
    distinanet.eval()  # Set model to evaluation mode
    if torch.cuda.is_available() and torch.cuda.device_count() > 1:
        distinanet = torch.nn.DataParallel(distinanet)
    
    
    # Create evaluator and run evaluation
    evaluator = ModelEvaluator(distinanet, device, score_threshold=parser.iou_threshold)
    
    # Create a simple dataloader for evaluation with num_workers=0 to avoid multiprocessing issues
    from torch.utils.data import DataLoader
    dataloader_val = DataLoader(dataset_val, batch_size=1, shuffle=False, num_workers=0, pin_memory=True if torch.cuda.is_available() else False)
    
    # Debug: Check data shape
    sample_data = next(iter(dataloader_val))
    logger.debug(f"Sample data shapes - img: {sample_data['img'].shape}, annot: {sample_data['annot'].shape}")
    
    # Run evaluation
    results = evaluator.evaluate_model(dataloader_val, save_path=parser.save_path)
    
    logger.info(f"Evaluation completed successfully!")
    logger.info(f"Results: {results}")

if __name__ == '__main__':
    # Set multiprocessing start method for CUDA compatibility
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass
    main()
