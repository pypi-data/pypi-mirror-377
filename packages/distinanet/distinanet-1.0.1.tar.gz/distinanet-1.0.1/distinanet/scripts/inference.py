import numpy as np
import torchvision
import time
import os
import copy
import pdb
import time
import argparse

import sys
import cv2

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, models, transforms

from distinanet.data.datasets import CSVDataset
from distinanet.data.collater import Collater
from distinanet.data.transforms import Resizer, Augmenter, Normalizer, UnNormalizer
from distinanet.data.samplers import AspectRatioBasedSampler
from distinanet.utils import setup_logger, get_device

logger = setup_logger("inference", "INFO")

assert torch.__version__.split('.')[0] == '1'

logger.info('CUDA available: {}'.format(torch.cuda.is_available()))
device = get_device()

def load_model_from_checkpoint(model_path, dataset):
    """Load model from checkpoint or complete model file"""
    logger.info(f"Loading model from: {model_path}")
    
    checkpoint = torch.load(model_path, map_location=device)
    
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        # Loading from checkpoint - need to reconstruct model
        logger.info("Loading from checkpoint file...")
        
        # Extract model configuration from checkpoint
        config_dict = checkpoint.get('config_dict', {})
        
        # Try to get number of classes from dataset, or detect from checkpoint
        if dataset is not None:
            num_classes = dataset.num_classes()
        else:
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

def main(args=None):
	parser = argparse.ArgumentParser(description='Simple inference script for Distinanet')

	parser.add_argument('--coco_path', help='Path to COCO directory')
	parser.add_argument('--csv_classes', help='Path to file containing class list (see readme)')
	parser.add_argument('--csv_val', help='Path to file containing validation annotations (optional, see readme)')
	parser.add_argument('--model', help='Path to model (.pt) file.')
	parser.add_argument('--save_path', help='Save path for results', type=str, default=None)

	parser = parser.parse_args(args)

	# Setup save path based on model path if not specified
	if parser.save_path is None and parser.model:
		# Try to extract run directory from model path
		model_path_parts = parser.model.split(os.sep)
		if 'runs' in model_path_parts:
			runs_idx = model_path_parts.index('runs')
			if runs_idx + 1 < len(model_path_parts):
				run_dir = os.path.join(*model_path_parts[:runs_idx+2])
				parser.save_path = os.path.join(run_dir, 'inference')
				os.makedirs(parser.save_path, exist_ok=True)
				logger.info(f"Results will be saved to: {parser.save_path}")

	# Create dataset with updated transforms
	dataset_val = CSVDataset(
		train_file=parser.csv_val, 
		class_list=parser.csv_classes, 
		transform=transforms.Compose([Normalizer(), Resizer()]), 
		device='cpu'  # Keep on CPU to avoid CUDA multiprocessing issues
	)

	# Use simple DataLoader like in test script instead of AspectRatioBasedSampler + Collater
	dataloader_val = DataLoader(dataset_val, batch_size=1, shuffle=False, num_workers=0, pin_memory=True if torch.cuda.is_available() else False)

	# Load model using the new checkpoint-aware function
	distinanet = load_model_from_checkpoint(parser.model, dataset_val)
	distinanet = distinanet.to(device)
	distinanet.eval()  # Set to evaluation mode

	unnormalize = UnNormalizer()

	def draw_caption(image, box, caption):

		b = np.array(box).astype(int)
		cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 4)
		cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

	def draw_caption_gt(image, box, caption):

		b = np.array(box).astype(int)
		cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 4)
		cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

	for idx, data in enumerate(dataloader_val):

		with torch.no_grad():
			st = time.time()
			# Move data to device
			img_tensor = data['img'].to(device).float()
			
			# Get model predictions - model returns [scores, classes, boxes, distances]
			outputs = distinanet(img_tensor)
			scores, classification, transformed_anchors, distances = outputs
			
			logger.info('Elapsed time: {}'.format(time.time()-st))
			idxs = np.where(scores.cpu()>0.5)
			img = np.array(255 * unnormalize(data['img'][0, :, :, :])).copy()

			img[img<0] = 0
			img[img>255] = 255

			img = np.transpose(img, (1, 2, 0))

			img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2RGB)

			for j in range(idxs[0].shape[0]):

				bbox = transformed_anchors[idxs[0][j], :]
				
				x1 = int(bbox[0])
				y1 = int(bbox[1])
				x2 = int(bbox[2])
				y2 = int(bbox[3])
				label_name = dataset_val.labels[int(classification[idxs[0][j]])]
				label_number = int(classification[idxs[0][j]])
				distance = round(distances[idxs[0]][j].item(),1) #[0] = item is repeated several times so we want only first, [idxs[0]] = all the idxs filtered by NMS, [j] = All the distance predictions
			
				draw_caption(img, (x1, y1, x2, y2), f"{str(label_name), distance}")

				cv2.rectangle(img, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)

				logger.info(f"Pred: {x1}, {y1}, {x2}, {y2}, {label_number}, {label_name}, {distance}")

			#Print and plot ground truth
			#print("GT no.:",data['annot'][0].shape[0])
			#print(data['annot'][0])

			for k in range(data['annot'][0].shape[0]):

				gt_x1 = int(data['annot'][0][k][0].item()) #[0] = empty_dimension, [k] = all the ground truth annotations, [0] = bbox coordinate x1
				gt_y1 = int(data['annot'][0][k][1].item())
				gt_x2 = int(data['annot'][0][k][2].item())
				gt_y2 = int(data['annot'][0][k][3].item())
				gt_label_number = int(data['annot'][0][k][4].item())
				gt_label = 'Car' if gt_label_number == 0 else 'Pedestrian' if gt_label_number == 1 else 'Truck'
				gt_distance = float(data['annot'][0][k][5].item())

				draw_caption_gt(img, (gt_x1, gt_y1, gt_x2, gt_y2), f"{gt_label}, {gt_distance:.2f}")

				cv2.rectangle(img, (gt_x1, gt_y1), (gt_x2, gt_y2), color=(0, 0, 255), thickness=2)

				logger.info(f"Ground Truth: {gt_x1}, {gt_y1}, {gt_x2}, {gt_y2}, {gt_label_number}, {gt_distance}")

			cv2.imshow('img', img)
			key = cv2.waitKey(0) & 0xFF  # Use mask for compatibility with different systems
			if key == ord('q'):
				break
			elif key == ord('s'):
				if not os.path.exists('inference_output'):
					os.makedirs('inference_output')
				cv2.imwrite(f'inference_output/{idx}.jpg', img)
			else:
				continue

if __name__ == '__main__':
 main()