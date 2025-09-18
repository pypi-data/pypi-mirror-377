import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from distinanet.utils import setup_logger
from evaluation_utils.metrics import mean_absolute_error

logger = setup_logger("csv_eval", "INFO")

def log_and_save_metrics(average_precisions, mae, mre, rmse, rmsle, mAP, mean_inference_time, generator, save_path):
    if save_path is not None:
        os.makedirs(save_path, exist_ok=True)
        logger.info(f"Created/verified save directory: {save_path}")

    metrics_list = []
    total_annotations = 0

    logger.info("\n-----Validation results------\n")
    logger.info(f'Distance MAE: {mae:.3f}')
    logger.info(f'Distance MRE: {mre:.3f}')
    logger.info(f'Distance RMSE: {rmse:.3f}')
    logger.info(f'Distance RMSLE: {rmsle:.3f}')
    logger.info(f'mAP: {mAP:.3f}')
    logger.info(f'Mean Inference Time: {mean_inference_time:.3f} seconds\n')

    for label in range(generator.num_classes()):
        label_name = generator.label_to_name(label)
        ap_cls, mae_cls, mre_cls, rmse_cls, rmsle_cls, num_annotations = [f'{val:.3f}' for val in average_precisions[label][:6]]

        metrics_list.append({
            'Class': label_name,
            'AP': ap_cls,
            'MAE': mae_cls,
            'MRE': mre_cls,
            'RMSE': rmse_cls,
            'RMSLE': rmsle_cls,
            '#': num_annotations
        })

        total_annotations += int(round(float(num_annotations)))

        logger.info(f'{label_name}: AP: {ap_cls}, MAE: {mae_cls}, MRE: {mre_cls}, RMSE: {rmse_cls}, RMSLE: {rmsle_cls}, No. annotations: {int(round(float(num_annotations)))}')

    metrics_list.append({
        'Class': 'Total',
        'AP': f'{mAP:.3f}',
        'MAE': f'{mae:.3f}',
        'MRE': f'{mre:.3f}',
        'RMSE': f'{rmse:.3f}',
        'RMSLE': f'{rmsle:.3f}',
        '#': int(round(total_annotations))
    })

    if save_path is not None:
        excel_path = os.path.join(save_path, 'evaluation_metrics.xlsx')
        logger.info(f"Saving evaluation results to {excel_path}")
        results_df = pd.DataFrame(metrics_list)
        results_df.to_excel(excel_path, index=False)

def plot_distance_mae(gt_distances, pred_distances, save_path):
    if save_path is not None:
        BIN_DIST = 5
        bins = np.arange(0, np.max(gt_distances) + BIN_DIST, BIN_DIST)
        mae_bins = []
        for i in range(len(bins) - 1):
            mask = np.logical_and(gt_distances >= bins[i], gt_distances < bins[i + 1])
            mae_bin = mean_absolute_error(pred_distances[mask], gt_distances[mask])
            mae_bins.append(mae_bin)
        
        plt.figure(figsize=(12, 6))
        plt.bar(bins[:-1] + (BIN_DIST - 0.1) / 2, mae_bins, width=(BIN_DIST - 0.1) * 0.65, align='center', edgecolor='black', linewidth=1.05)
        plt.xlabel('Distance Range (m)')
        plt.ylabel('Mean Absolute Error')
        plt.title('Mean Absolute Error by Distance Range (DistinaNet)', fontsize=20)
        for bin_edge in bins[1:-1]:
            plt.axvline(x=bin_edge, color='black', linestyle='--', linewidth=0.8)
        plt.xticks(np.arange(0, np.max(bins), BIN_DIST))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(save_path, 'distwise_mae_distinanet.jpg'), dpi=300)
        plt.close()

def plot_precision_recall(recall, precision, label_name, save_path):
    if save_path is not None:
        plt.plot(recall, precision)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision Recall Curve ({label_name})')
        plt.savefig(os.path.join(save_path, f'{label_name}_precision_recall.jpg'))
        plt.close()
