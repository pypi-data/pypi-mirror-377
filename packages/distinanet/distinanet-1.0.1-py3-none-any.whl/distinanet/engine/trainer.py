import torch
import numpy as np
import time
import datetime
import math
import collections
import os

from evaluation_utils.evaluator import evaluate_model
from training_utils.checkpoint_manager import save_checkpoint

def train_one_epoch(epoch_num, dataloader_train, distinanet, optimizer, writer, logger, args, no_iter):
    distinanet.train()
    if hasattr(distinanet, 'module'):
        distinanet.module.freeze_bn()
    else:
        distinanet.freeze_bn()

    epoch_loss = []
    epoch_classification_loss = []
    epoch_regression_loss = []
    epoch_distance_loss = []
    loss_hist = collections.deque(maxlen=500)

    for iter_num, data in enumerate(dataloader_train):
        try:
            optimizer.zero_grad()

            imgs = data['img'].to(args.device).float()
            annots = data['annot'].to(args.device)

            classification_loss, regression_loss, distance_loss = distinanet((imgs, annots))
                
            classification_loss = classification_loss.mean()
            regression_loss = regression_loss.mean()
            distance_loss = distance_loss.mean()

            loss = classification_loss + regression_loss + args.distance_weight * distance_loss

            if bool(loss == 0):
                continue

            loss.backward()
            torch.nn.utils.clip_grad_norm_(distinanet.parameters(), 0.1)
            optimizer.step()

            loss_hist.append(float(loss))
            epoch_loss.append(float(loss))

            # Log iteration losses
            writer.add_scalar('Loss/Classification', float(classification_loss), epoch_num * len(dataloader_train) + iter_num)
            writer.add_scalar('Loss/Regression', float(regression_loss), epoch_num * len(dataloader_train) + iter_num)
            writer.add_scalar('Loss/Distance', float(distance_loss), epoch_num * len(dataloader_train) + iter_num)
            writer.add_scalar('Loss/TotalLoss', float(loss), epoch_num * len(dataloader_train) + iter_num)

            epoch_classification_loss.append(float(classification_loss))
            epoch_regression_loss.append(float(regression_loss))
            epoch_distance_loss.append(float(distance_loss))

            logger.info(
                'Epoch: {} | Iteration: {}/{} | Classification loss: {:1.5f} | Regression loss: {:1.5f} | Distance loss: {:1.5f} | Running loss: {:1.5f}'.format(
                    epoch_num, iter_num, no_iter, float(classification_loss), float(regression_loss), float(distance_loss), np.mean(loss_hist)))

            del classification_loss, regression_loss, distance_loss
        except Exception as e:
            logger.error(f"Error in training iteration: {e}")
            continue
            
    return {
        "epoch_loss": np.mean(epoch_loss),
        "epoch_classification_loss": np.mean(epoch_classification_loss),
        "epoch_regression_loss": np.mean(epoch_regression_loss),
        "epoch_distance_loss": np.mean(epoch_distance_loss)
    }

def evaluate_and_log(epoch_num, dataset_val, distinanet, writer, logger, best_mAP, best_mae, best_epoch_mAP, best_epoch_mae):
    logger.info('Evaluating dataset')
    mAP, mae = evaluate_model(dataset_val, distinanet)

    writer.add_scalar('Epoch_val_MAE', mae, epoch_num)
    writer.add_scalar('Epoch_val_mAP', mAP, epoch_num)

    if (best_mae is None) or (mae <= best_mae):
        logger.info("MAE results improved in this epoch. Saving best MAE.")
        best_mae = mae
        best_epoch_mae = epoch_num

    if (best_mAP is None) or (mAP >= best_mAP):
        logger.info("mAP results improved in this epoch. Saving best mAP.")
        best_mAP = mAP
        best_epoch_mAP = epoch_num
        
    return mAP, mae, best_mAP, best_mae, best_epoch_mAP, best_epoch_mae

def log_epoch_metrics(writer, epoch_num, losses):
    writer.add_scalar('Epoch_Loss/Classification', losses["epoch_classification_loss"], epoch_num)
    writer.add_scalar('Epoch_Loss/Regression', losses["epoch_regression_loss"], epoch_num)
    writer.add_scalar('Epoch_Loss/Distance', losses["epoch_distance_loss"], epoch_num)
    writer.add_scalar('Epoch_Loss/TotalLoss', losses["epoch_loss"], epoch_num)

def save_training_details(log_dir, args, num_params, epoch_num, mAP, mae, best_epoch_mAP, best_mAP, best_epoch_mae, best_mae, total_training_time_str):
    with open(os.path.join(log_dir, "training_details.txt"), "w") as file:
        file.write(f"Training Time: {total_training_time_str}\n")
        file.write(f"Batch Size: {args.batch_size}\n")
        file.write(f"Number of parameters: {num_params}\n")
        file.write(f"Epochs: {epoch_num+1}\n\n")
        file.write(f"Last validation mAP: {mAP}\n")
        file.write(f"Last validation MAE: {mae}\n\n")
        file.write(f"Best validation mAP Epoch: {best_epoch_mAP}\n")
        file.write(f"Best validation mAP: {best_mAP}\n\n")
        file.write(f"Best validation MAE Epoch: {best_epoch_mae}\n")
        file.write(f"Best validation MAE: {best_mae}\n\n")
