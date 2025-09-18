import cv2
import numpy as np
import torch
import argparse
from torchvision import transforms
import time
from PIL import Image
import os

from distinanet.utils import setup_logger, get_device
logger = setup_logger("video", "INFO")

def draw_caption(image, box, caption):
    b = np.array(box).astype(int)
    cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

def load_model_from_checkpoint(model_path, device):
    """Load model from checkpoint or complete model file"""
    logger.info(f"Loading model from: {model_path}")
    
    checkpoint = torch.load(model_path, map_location=device)
    
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        # Loading from checkpoint - need to reconstruct model
        logger.info("Loading from checkpoint file...")
        
        # Extract model configuration from checkpoint
        config_dict = checkpoint.get('config_dict', {})
        
        # Try to determine number of classes from the checkpoint state dict
        num_classes = 80  # Default fallback
        state_dict = checkpoint['model_state_dict']
        
        # Look for classification layer to determine number of classes
        if 'classificationModel.output.bias' in state_dict:
            # Each class has 9 outputs (for anchors), so divide by 9
            total_outputs = state_dict['classificationModel.output.bias'].shape[0]
            num_classes = total_outputs // 9
            logger.info(f"Detected {num_classes} classes from checkpoint")
        
        # Import and create model
        from distinanet.model.model import DistinaNet
        distinanet = DistinaNet(
            num_classes=num_classes,
            backbone_depth=config_dict.get('depth', 18),
            pretrained=False,
            distance_head_type=config_dict.get('distance_head_type', 'base'),
            distance_loss_type=config_dict.get('distance_loss_type', 'huber')
        )
        
        # Load the saved state dict
        distinanet.load_state_dict(checkpoint['model_state_dict'])
        distinanet = distinanet.to(device)  # Move to correct device
        logger.info(f"Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
        
    else:
        # Loading complete model file (legacy)
        logger.info("Loading complete model file...")
        distinanet = checkpoint
        distinanet = distinanet.to(device)  # Move to correct device
    
    return distinanet

class VideoFrameProcessor(object):
    def __init__(self):
        self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    def process_frame(self, frame):
        # Convert frame to PIL Image
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)

        # Resize frame to ensure dimensions are multiples of 32
        original_width, original_height = frame.size
        new_width = 32 * ((original_width // 32) + (1 if original_width % 32 != 0 else 0))
        new_height = 32 * ((original_height // 32) + (1 if original_height % 32 != 0 else 0))
        frame = frame.resize((new_width, new_height))

        # Apply transformations similar to your dataset preprocessing
        frame = transforms.ToTensor()(frame)
        frame = self.normalize(frame)
        frame = frame.unsqueeze(0)  # Add batch dimension
        
        # If using CUDA
        if torch.cuda.is_available():
            frame = frame.cuda()
        
        return frame


def main(args=None):
    parser = argparse.ArgumentParser(description='Script for processing video with DistinaNet.')
    parser.add_argument('--video_path', required=True, help='Path to the video file.')
    parser.add_argument('--model_path', required=True, help='Path to model (.pt) file.')
    parser.add_argument('--output_path', help='Path for the output video.')
    parser.add_argument('--save_dir', help='Directory to save results (auto-detects from model path if not specified)')
    args = parser.parse_args(args)

    # Get device
    device = get_device()

    # Setup save directory based on model path if not specified
    if args.save_dir is None and args.output_path is None:
        # Try to extract run directory from model path
        model_path_parts = args.model_path.split(os.sep)
        if 'runs' in model_path_parts:
            runs_idx = model_path_parts.index('runs')
            if runs_idx + 1 < len(model_path_parts):
                run_dir = os.path.join(*model_path_parts[:runs_idx+2])
                args.save_dir = os.path.join(run_dir, 'video')
                os.makedirs(args.save_dir, exist_ok=True)
                # Set default output path in the run directory
                video_name = os.path.splitext(os.path.basename(args.video_path))[0]
                args.output_path = os.path.join(args.save_dir, f'{video_name}_output.mp4')
                logger.info(f"Results will be saved to: {args.output_path}")
    elif args.output_path is None:
        # Use save_dir if specified
        video_name = os.path.splitext(os.path.basename(args.video_path))[0]
        args.output_path = os.path.join(args.save_dir, f'{video_name}_output.mp4')
    
    
    # Load model
    distinanet = load_model_from_checkpoint(args.model_path, device)
    distinanet.eval()
    distinanet = distinanet.to(device)  # Ensure model is on correct device
    
    # Open input video
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {args.video_path}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    logger.info(f"Input video: {width}x{height}, {fps} FPS, {total_frames} frames")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    
    # Ensure output path has proper extension for MJPG codec
    if not args.output_path.lower().endswith('.avi'):
        args.output_path += '.avi'
        logger.info(f"Added .avi extension: {args.output_path}")
    
    # Create video writer - MJPG works reliably
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(args.output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        logger.error(f"Cannot create output video: {args.output_path}")
        cap.release()
        return
    
    # Process frames
    video_processor = VideoFrameProcessor()
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        start_time = time.time()
        frame_count += 1
        logger.info(f"Processing frame {frame_count}/{total_frames}...")

        # Process frame using the video frame processor
        processed_frame = video_processor.process_frame(frame)
        
        with torch.no_grad():
            scores, classification, transformed_anchors, distances = distinanet(processed_frame)
        
        # Draw predictions
        idxs = np.where(scores.cpu() > 0.5)
        for j in range(len(idxs[0])):
            bbox = transformed_anchors[idxs[0][j], :].cpu().numpy()
            x1, y1, x2, y2 = bbox.astype(int)
            label = f'Class {classification[idxs[0][j]]}'
            distance = distances[idxs[0][j]].cpu().numpy()

            draw_caption(frame, (x1, y1, x2, y2), f"{distance[0]:.2f}m")
            cv2.rectangle(frame, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)

        # Calculate and display FPS
        inference_time = (time.time() - start_time)
        cv2.putText(frame, f"Inference time: {inference_time:.2f} s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Write the frame
        out.write(frame)
        
        if frame_count % 100 == 0:
            logger.info(f"Processed {frame_count}/{total_frames} frames")
    
    # Cleanup
    cap.release()
    out.release()
    
    logger.info(f"Video processing complete: {args.output_path}")
    logger.info(f"Output file size: {os.path.getsize(args.output_path)} bytes")

if __name__ == '__main__':
    main()
