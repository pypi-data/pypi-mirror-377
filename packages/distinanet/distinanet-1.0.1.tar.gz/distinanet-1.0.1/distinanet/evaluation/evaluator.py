"""
Model Evaluator for DistinaNet

This module provides the main evaluation functionality for DistinaNet models.
It orchestrates the entire evaluation process:
1. Extracting model predictions and ground truth annotations
2. Computing evaluation metrics (mAP, distance metrics)
3. Generating and saving evaluation results

This is the main entry point for model evaluation and validation.
"""

from __future__ import print_function

import numpy as np
from distinanet.utils import setup_logger
from evaluation_utils.metrics import (
    compute_ap,
    mean_absolute_error,
    mean_relative_error,
    root_mean_squared_error,
    log_root_mean_squared_error,
    compute_overlap
)
from evaluation_utils.evaluation_inference_engine import extract_model_predictions, extract_ground_truth_annotations
from evaluation_utils.results_handler import log_and_save_metrics, plot_distance_mae, plot_precision_recall

logger = setup_logger("evaluation", "INFO")

def evaluate_model(dataset, distinanet, iou_threshold=0.5, score_threshold=0.05, max_detections=100, save_path=None):
    """
    Comprehensive evaluation of a DistinaNet model on a given dataset.
    
    This function orchestrates the complete evaluation process:
    1. Extracts model predictions and ground truth annotations
    2. Computes detection metrics (mAP) and distance estimation metrics
    3. Logs results and saves plots/reports if requested
    
    Args:
        dataset: The dataset to evaluate on
        distinanet: The trained DistinaNet model
        iou_threshold: IoU threshold for considering detections as true positives
        score_threshold: Confidence threshold for detections
        max_detections: Maximum detections per image
        save_path: Optional path to save evaluation plots and results
        
    Returns:
        tuple: (mAP, mae) - Mean Average Precision and Mean Absolute Error
    """
    # Extract model predictions and ground truth data
    all_detections, mean_inference_time = extract_model_predictions(
        dataset, distinanet, score_threshold=score_threshold, max_detections=max_detections
    )
    all_annotations = extract_ground_truth_annotations(dataset)
    # Initialize evaluation metrics storage
    average_precisions = {}
    gt_distances = []
    pred_distances = []
    map_values = []

    # Evaluate each class separately
    for label in range(dataset.num_classes()):
        false_positives = np.zeros((0,))
        true_positives  = np.zeros((0,))
        scores          = np.zeros((0,))
        num_annotations = 0.0
        class_gt_distances = []
        class_pred_distances = []

        for i in range(len(dataset)):
            detections = all_detections[i][label]
            annotations = all_annotations[i][label]
            num_annotations += annotations.shape[0]
            detected_annotations = []

            for d in detections:
                scores = np.append(scores, d[4])

                if annotations.shape[0] == 0:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)
                    continue

                overlaps = compute_overlap(np.expand_dims(d, axis=0), annotations)
                assigned_annotation = np.argmax(overlaps, axis=1)
                max_overlap = overlaps[0, assigned_annotation]

                if max_overlap >= iou_threshold and assigned_annotation not in detected_annotations:
                    false_positives = np.append(false_positives, 0)
                    true_positives  = np.append(true_positives, 1)
                    detected_annotations.append(assigned_annotation)
                    pred_distances.append(d[5])
                    gt_distances.append(annotations[assigned_annotation][0][5])
                    class_pred_distances.append(d[5])
                    class_gt_distances.append(annotations[assigned_annotation][0][5])
                else:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)

        if num_annotations == 0:
            average_precisions[label] = 0, 0, 0, 0, 0, 0
            continue
            
        indices = np.argsort(-scores)
        false_positives = false_positives[indices]
        true_positives  = true_positives[indices]

        false_positives = np.cumsum(false_positives)
        true_positives  = np.cumsum(true_positives)

        recall    = true_positives / num_annotations
        precision = true_positives / np.maximum(true_positives + false_positives, np.finfo(np.float64).eps)

        average_precision  = compute_ap(recall, precision)
        
        class_pred_distances = np.array(class_pred_distances)
        class_gt_distances = np.array(class_gt_distances)

        class_mae = mean_absolute_error(class_gt_distances, class_pred_distances)
        class_mre = mean_relative_error(class_gt_distances, class_pred_distances)
        class_rmse = root_mean_squared_error(class_gt_distances, class_pred_distances)
        class_rmsle = log_root_mean_squared_error(class_gt_distances, class_pred_distances)

        map_values.append(average_precision)
        average_precisions[label] = average_precision, class_mae, class_mre, class_rmse, class_rmsle, num_annotations

        if save_path is not None:
            plot_precision_recall(recall, precision, dataset.label_to_name(label), save_path)

    # Compute overall evaluation metrics
    gt_distances = np.array(gt_distances)
    pred_distances = np.array(pred_distances)

    mae = mean_absolute_error(pred_distances, gt_distances)
    mre = mean_relative_error(pred_distances, gt_distances)
    rmse = root_mean_squared_error(pred_distances, gt_distances)
    rmsle = log_root_mean_squared_error(pred_distances, gt_distances)
    mAP = np.mean(map_values)

    # Log results and save plots/reports
    log_and_save_metrics(average_precisions, mae, mre, rmse, rmsle, mAP, mean_inference_time, dataset, save_path)
    
    if save_path is not None:
        plot_distance_mae(gt_distances, pred_distances, save_path)

    return mAP, mae