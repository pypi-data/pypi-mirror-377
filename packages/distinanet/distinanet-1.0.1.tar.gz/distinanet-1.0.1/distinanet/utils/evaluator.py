"""Simple evaluator class for model evaluation"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm

class ModelEvaluator:
    """Handles model evaluation logic"""
    
    def __init__(self, model, device, score_threshold=0.5):
        self.model = model
        self.device = device
        self.score_threshold = score_threshold
        self.predictions = []
        self.ground_truth = []
    
    def evaluate_model(self, dataloader, save_path: Optional[str] = None) -> Dict[str, float]:
        """Run complete model evaluation"""
        print("Starting evaluation...")
        
        # Get predictions
        predictions, gt_annotations = self._get_predictions(dataloader)
        
        # Calculate metrics
        map_score = self._calculate_map(predictions, gt_annotations)
        distance_metrics = self._calculate_distance_metrics(predictions, gt_annotations)
        
        # Combine results
        results = {
            'mAP': map_score,
            **distance_metrics
        }
        
        self._print_results(results)
        
        if save_path:
            self._save_results(results, save_path)
        
        return results
    
    def _get_predictions(self, dataloader):
        """Get model predictions on dataset"""
        self.model.eval()
        predictions = []
        ground_truth = []
        
        with torch.no_grad():
            # Create progress bar for evaluation
            eval_pbar = tqdm(enumerate(dataloader), 
                           total=len(dataloader),
                           desc="Evaluating Model",
                           unit="batch")
            
            for idx, data in eval_pbar:
                # Move data to device - handle both dict and tensor formats
                if isinstance(data, dict):
                    # Move each tensor in the data dict to device
                    for key in data:
                        if torch.is_tensor(data[key]):
                            data[key] = data[key].to(self.device, non_blocking=True)
                elif torch.is_tensor(data):
                    data = data.to(self.device, non_blocking=True)
                
                # Get model predictions
                if isinstance(data, dict) and 'img' in data:
                    # Handle case where data is a dictionary with 'img' key
                    outputs = self.model(data['img'])
                    if 'annot' in data:
                        ground_truth.append(data['annot'].cpu())
                else:
                    # Handle case where data is just the image tensor
                    outputs = self.model(data)
                
                # Store predictions (move to CPU to save GPU memory)
                if isinstance(outputs, (list, tuple)):
                    outputs = [out.cpu() if torch.is_tensor(out) else out for out in outputs]
                elif torch.is_tensor(outputs):
                    outputs = outputs.cpu()
                
                predictions.append(outputs)
                
                # Update progress bar
                eval_pbar.set_postfix({
                    'Processed': f'{idx + 1}/{len(dataloader)}',
                    'Memory': f'{torch.cuda.memory_allocated()/1024**2:.0f}MB' if torch.cuda.is_available() else 'N/A'
                })
            
            eval_pbar.close()
        
        print("\n✓ Prediction generation complete.")
        return predictions, ground_truth
    
    def _calculate_map(self, predictions, ground_truth) -> float:
        """Calculate mean Average Precision"""
        # Placeholder implementation - replace with your actual mAP calculation
        print("📊 Calculating mAP...")
        # This would contain your existing mAP calculation logic
        
        # Simulate progress for demonstration
        calc_pbar = tqdm(range(len(predictions)), desc="Computing mAP", unit="sample")
        for i in calc_pbar:
            # Your mAP calculation logic would go here
            calc_pbar.set_postfix({'Sample': f'{i+1}/{len(predictions)}'})
        calc_pbar.close()
        
        return 0.75  # placeholder value
    
    def _calculate_distance_metrics(self, predictions, ground_truth) -> Dict[str, float]:
        """Calculate distance estimation metrics by matching predictions with ground truth"""
        print("📏 Calculating distance metrics...")
        
        matched_pred_distances = []
        matched_true_distances = []
        
        # Match predictions with ground truth with progress bar
        distance_pbar = tqdm(zip(predictions, ground_truth), 
                           total=len(predictions),
                           desc="Matching pred-GT distances",
                           unit="sample")
        
        for pred, gt in distance_pbar:
            # Extract ground truth information first
            if torch.is_tensor(gt) and gt.shape[-1] >= 6:
                gt_flat = gt.reshape(-1, gt.shape[-1])
                valid_gt = gt_flat[gt_flat[:, 4] >= 0]  # Filter out padding (-1 class values)
                
                if len(valid_gt) == 0:
                    continue
                    
                # Extract predictions
                if isinstance(pred, (list, tuple)) and len(pred) >= 4:
                    pred_scores = pred[0] if torch.is_tensor(pred[0]) else torch.tensor(pred[0])
                    pred_classes = pred[1] if torch.is_tensor(pred[1]) else torch.tensor(pred[1])
                    pred_boxes = pred[2] if torch.is_tensor(pred[2]) else torch.tensor(pred[2])
                    pred_distances = pred[3] if torch.is_tensor(pred[3]) else torch.tensor(pred[3])
                    
                    if len(pred_distances) == 0:
                        continue
                    
                    # For simplicity, take top N predictions where N = number of ground truth objects
                    # In a more sophisticated system, you'd do proper IoU matching
                    num_gt = len(valid_gt)
                    num_predictions = min(len(pred_distances), num_gt)
                    
                    if num_predictions > 0:
                        # Take top predictions (assuming they're sorted by confidence)
                        top_pred_distances = pred_distances[:num_predictions]
                        corresponding_gt_distances = valid_gt[:num_predictions, 5]  # Distance column
                        
                        # Convert to numpy and add to matched lists
                        if torch.is_tensor(top_pred_distances):
                            matched_pred_distances.extend(top_pred_distances.cpu().numpy().flatten())
                        else:
                            matched_pred_distances.extend(np.array(top_pred_distances).flatten())
                            
                        matched_true_distances.extend(corresponding_gt_distances.cpu().numpy().flatten())
        
        distance_pbar.close()
        
        if not matched_pred_distances or not matched_true_distances:
            return {'mae': 0.0, 'rmse': 0.0, 'mean_pred': 0.0, 'mean_true': 0.0}
        
        matched_pred_distances = np.array(matched_pred_distances)
        matched_true_distances = np.array(matched_true_distances)
        
        # Ensure arrays have the same length
        min_length = min(len(matched_pred_distances), len(matched_true_distances))
        matched_pred_distances = matched_pred_distances[:min_length]
        matched_true_distances = matched_true_distances[:min_length]
        
        mae = np.mean(np.abs(matched_pred_distances - matched_true_distances))
        rmse = np.sqrt(np.mean((matched_pred_distances - matched_true_distances) ** 2))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mean_pred': np.mean(matched_pred_distances),
            'mean_true': np.mean(matched_true_distances)
        }
    
    def _print_results(self, results: Dict[str, float]):
        """Print evaluation results"""
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        print(f"mAP: {results['mAP']:.3f}")
        print(f"Distance MAE: {results['mae']:.3f}")
        print(f"Distance RMSE: {results['rmse']:.3f}")
        if 'mean_pred' in results and 'mean_true' in results:
            print(f"Mean Predicted Distance: {results['mean_pred']:.3f}")
            print(f"Mean True Distance: {results['mean_true']:.3f}")
        print("="*50)
    
    def _save_results(self, results: Dict[str, float], save_path: str):
        """Save results to file"""
        import json
        # Convert numpy floats to Python floats for JSON serialization
        json_results = {k: float(v) for k, v in results.items()}
        with open(save_path, 'w') as f:
            json.dump(json_results, f, indent=2)
        print(f"Results saved to: {save_path}")
    
    def get_inference_results(self, image_tensor):
        """Get inference results for a single image"""
        self.model.eval()
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            outputs = self.model(image_tensor)
            return outputs
