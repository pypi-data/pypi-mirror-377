import torch
import torch.multiprocessing as mp
import time
import datetime
import math
import os
from tqdm import tqdm

# Set multiprocessing start method for CUDA compatibility
try:
    mp.set_start_method('spawn', force=True)
except RuntimeError:
    pass

from distinanet.config import Config, ConfigParser
from distinanet.utils import Trainer, setup_logger, create_run_directory, print_model_summary
from distinanet.engine.dataloader_setup import get_training_dataloaders
from distinanet.model.model import DistinaNet

def main():
    """
    Main training loop for the distinanet model.
    """
    # Get configuration using new system
    config = ConfigParser.parse_args()

    # Create timestamped run directory for organized outputs
    run_dir = create_run_directory()
    logger = setup_logger("training", "INFO")
    
    # Create trainer with run directory
    trainer = Trainer(config, run_dir)
    trainer.print_training_info()

    # Get dataloaders
    dataloader_train, dataloader_val, dataset_train, dataset_val = get_training_dataloaders(config, logger)

    # Build model directly
    logger.info(f"Building model with depth: {config.depth}")
    pretrained_flag = not config.load_checkpoint
    
    distinanet = DistinaNet(
        num_classes=dataset_train.num_classes(),
        backbone_depth=config.depth,
        pretrained=pretrained_flag,
        distance_head_type=config.distance_head_type,
        distance_loss_type=config.distance_loss_type
    )

    distinanet.to(config.device)
    logger.info("Model created and moved to device.")
    
    # Print model summary
    print_model_summary(distinanet)

    # Setup optimizer using trainer
    optimizer = trainer.create_optimizer(distinanet)
    
    # Load checkpoint if available using trainer
    start_epoch = trainer.load_checkpoint(distinanet, optimizer)

    # Parallelize model
    if config.num_gpus > 1:
        distinanet = torch.nn.DataParallel(distinanet, device_ids=[i for i in range(config.num_gpus)])
    distinanet.training = True

    # Log training info
    num_params = sum(p.numel() for p in distinanet.parameters() if p.requires_grad)
    logger.info(f"Number of trainable parameters in the model: {num_params}")
    logger.info(f'Dataset size: {len(dataset_train)}')
    no_iter = math.ceil(len(dataset_train) / config.batch_size)
    logger.info(f"Number of epochs: {config.epochs}")
    logger.info(f'Iterations per epoch: {no_iter}')
    
    training_start_time = time.time()
    
    # Initialize best metrics for model saving (use distance loss as primary criteria)
    best_val_dist_loss = float('inf')  # Lower is better for distance loss
    best_val_map = 0.0
    best_val_mae = float('inf')
    best_epoch = 0

    # Create epoch progress bar with color
    epoch_pbar = tqdm(range(start_epoch, config.epochs), 
                      desc="Training Progress", 
                      unit="epoch",
                      position=0,
                      leave=True,
                      colour='green')

    for epoch_num in epoch_pbar:
        epoch_start_time = time.time()
        
        # Update epoch progress bar description
        epoch_pbar.set_description(f"🚀 Epoch {epoch_num + 1}/{config.epochs}")

        # TRAINING PHASE
        distinanet.train()
        train_loss = 0.0
        train_cls_loss = 0.0
        train_reg_loss = 0.0
        train_dist_loss = 0.0
        
        # Create iteration progress bar for training
        iter_pbar = tqdm(enumerate(dataloader_train), 
                        total=len(dataloader_train),
                        desc=f"📚 Training",
                        unit="batch",
                        position=1,
                        leave=False,
                        colour='blue')
        
        for iter_num, data in iter_pbar:
            # Move data to device
            data['img'] = data['img'].to(config.device)
            data['annot'] = data['annot'].to(config.device)
            
            # Debug: Print tensor shape before any processing
            if iter_num == 0:  # Only print on first iteration to avoid spam
                logger.debug(f"Input tensor shape: {data['img'].shape}")
            
            # Ensure tensor is in correct format (B, C, H, W)
            if data['img'].dim() == 4:
                batch_size, dim1, dim2, dim3 = data['img'].shape
                
                # Expected format is (B, C, H, W) where C should be 3 for RGB
                if dim1 == 3:  # Already in correct format (B, C, H, W)
                    pass
                elif dim3 == 3:  # Format is (B, H, W, C) - need to permute to (B, C, H, W)
                    data['img'] = data['img'].permute(0, 3, 1, 2)
                    if iter_num == 0:
                        logger.debug(f"Permuted from (B,H,W,C) to (B,C,H,W): {data['img'].shape}")
                elif dim2 == 3:  # Format is (B, W, C, H) - need to permute to (B, C, H, W)
                    data['img'] = data['img'].permute(0, 2, 3, 1)
                    if iter_num == 0:
                        logger.debug(f"Permuted from (B,W,C,H) to (B,C,H,W): {data['img'].shape}")
                else:
                    logger.error(f"Unexpected tensor shape: {data['img'].shape}. Expected 3 channels in one of the dimensions.")
                    raise ValueError(f"Input tensor has unexpected shape: {data['img'].shape}")
                
                # Final validation
                if data['img'].shape[1] != 3:
                    logger.error(f"After permutation, tensor still has {data['img'].shape[1]} channels instead of 3")
                    raise ValueError(f"Input tensor has {data['img'].shape[1]} channels, expected 3")
            
            optimizer.zero_grad()
            
            # Forward pass - fix: pass img and annot as a tuple for training mode
            classification_loss, regression_loss, distance_loss = distinanet((data['img'], data['annot']))
            
            classification_loss = classification_loss.mean()
            regression_loss = regression_loss.mean()
            distance_loss = distance_loss.mean()
            
            loss = classification_loss + regression_loss + config.distance_weight * distance_loss
            
            if bool(loss == 0):
                continue
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(distinanet.parameters(), 0.1)
            optimizer.step()
            
            # Accumulate losses
            train_loss += loss.item()
            train_cls_loss += classification_loss.item()
            train_reg_loss += regression_loss.item()
            train_dist_loss += distance_loss.item()
            
            # Update iteration progress bar (cleaner version)
            iter_pbar.set_postfix({
                'Total_Avg': f'{train_loss/(iter_num+1):.4f}',
                'Cls': f'{train_cls_loss/(iter_num+1):.4f}',
                'Reg': f'{train_reg_loss/(iter_num+1):.4f}',
                'Dist': f'{train_dist_loss/(iter_num+1):.4f}'
            })
        
        # Close training iteration progress bar
        iter_pbar.close()
        
        # Calculate average training losses
        avg_train_loss = train_loss / len(dataloader_train)
        avg_train_cls = train_cls_loss / len(dataloader_train)
        avg_train_reg = train_reg_loss / len(dataloader_train)
        avg_train_dist = train_dist_loss / len(dataloader_train)
        
        # VALIDATION PHASE
        if dataloader_val is not None:
            # Keep model in training mode for loss computation, but disable gradients
            val_loss = 0.0
            val_cls_loss = 0.0
            val_reg_loss = 0.0
            val_dist_loss = 0.0
            
            # Create validation progress bar
            val_pbar = tqdm(enumerate(dataloader_val),
                           total=len(dataloader_val),
                           desc=f"🔍 Validation",
                           unit="batch",
                           position=1,
                           leave=False,
                           colour='yellow')
            
            with torch.no_grad():
                for val_iter, data in val_pbar:
                    # Move data to device
                    data['img'] = data['img'].to(config.device)
                    data['annot'] = data['annot'].to(config.device)
                    
                    # Ensure tensor is in correct format (B, C, H, W)
                    if data['img'].dim() == 4:
                        batch_size, dim1, dim2, dim3 = data['img'].shape
                        
                        # Expected format is (B, C, H, W) where C should be 3 for RGB
                        if dim1 == 3:  # Already in correct format (B, C, H, W)
                            pass
                        elif dim3 == 3:  # Format is (B, H, W, C) - need to permute to (B, C, H, W)
                            data['img'] = data['img'].permute(0, 3, 1, 2)
                        elif dim2 == 3:  # Format is (B, W, C, H) - need to permute to (B, C, H, W)
                            data['img'] = data['img'].permute(0, 2, 3, 1)
                        else:
                            logger.error(f"Validation: Unexpected tensor shape: {data['img'].shape}")
                            raise ValueError(f"Validation: Input tensor has unexpected shape: {data['img'].shape}")
                        
                        # Final validation
                        if data['img'].shape[1] != 3:
                            logger.error(f"Validation: After permutation, tensor still has {data['img'].shape[1]} channels instead of 3")
                            raise ValueError(f"Validation: Input tensor has {data['img'].shape[1]} channels, expected 3")
                    
                    # Forward pass - fix: pass img and annot as a tuple for training mode
                    classification_loss, regression_loss, distance_loss = distinanet((data['img'], data['annot']))
                    
                    classification_loss = classification_loss.mean()
                    regression_loss = regression_loss.mean()
                    distance_loss = distance_loss.mean()
                    
                    loss = classification_loss + regression_loss + config.distance_weight * distance_loss
                    
                    # Accumulate validation losses
                    val_loss += loss.item()
                    val_cls_loss += classification_loss.item()
                    val_reg_loss += regression_loss.item()
                    val_dist_loss += distance_loss.item()
                    
                    # Update validation progress bar
                    val_pbar.set_postfix({
                        'Val_Avg': f'{val_loss/(val_iter+1):.4f}',
                        'Val_Cls': f'{val_cls_loss/(val_iter+1):.4f}',
                        'Val_Reg': f'{val_reg_loss/(val_iter+1):.4f}',
                        'Val_Dist': f'{val_dist_loss/(val_iter+1):.4f}'
                    })
            
            val_pbar.close()
            
            # Calculate average validation losses
            avg_val_loss = val_loss / len(dataloader_val)
            avg_val_cls = val_cls_loss / len(dataloader_val)
            avg_val_reg = val_reg_loss / len(dataloader_val)
            avg_val_dist = val_dist_loss / len(dataloader_val)
            
            # For now, use validation loss as proxy for mAP (you can replace with actual mAP calculation)
            val_map = 1.0 / (1.0 + avg_val_loss)  # Simple proxy - replace with actual mAP
            val_mae = avg_val_dist  # Use distance loss as proxy for MAE
            
        else:
            # No validation data available
            avg_val_loss = avg_val_cls = avg_val_reg = avg_val_dist = 0.0
            val_map = val_mae = 0.0
        
        # Log all metrics to tensorboard
        trainer.log_metrics(epoch_num, avg_train_loss, val_map, val_mae)
        
        # Additional tensorboard logging
        if trainer.writer:
            # Training losses
            trainer.writer.add_scalar('Loss/Train_Total', avg_train_loss, epoch_num)
            trainer.writer.add_scalar('Loss/Train_Classification', avg_train_cls, epoch_num)
            trainer.writer.add_scalar('Loss/Train_Regression', avg_train_reg, epoch_num)
            trainer.writer.add_scalar('Loss/Train_Distance', avg_train_dist, epoch_num)
            
            # Validation losses (if available)
            if dataloader_val is not None:
                trainer.writer.add_scalar('Loss/Val_Total', avg_val_loss, epoch_num)
                trainer.writer.add_scalar('Loss/Val_Classification', avg_val_cls, epoch_num)
                trainer.writer.add_scalar('Loss/Val_Regression', avg_val_reg, epoch_num)
                trainer.writer.add_scalar('Loss/Val_Distance', avg_val_dist, epoch_num)
                trainer.writer.add_scalar('Metrics/Val_mAP_Proxy', val_map, epoch_num)
                trainer.writer.add_scalar('Metrics/Val_MAE_Proxy', val_mae, epoch_num)
            
            # Learning rate
            trainer.writer.add_scalar('Learning_Rate', optimizer.param_groups[0]['lr'], epoch_num)
        
        # Calculate epoch timing
        epoch_time = time.time() - epoch_start_time
        
        # Check if this is the best model so far (based on distance loss - lower is better)
        is_best = False
        if dataloader_val is not None:
            if avg_val_dist < best_val_dist_loss:
                best_val_dist_loss = avg_val_dist
                best_val_map = val_map  # Still track for logging
                best_epoch = epoch_num
                is_best = True
                
        # Save checkpoint (always save latest, and best separately)
        trainer.save_checkpoint(distinanet, optimizer, epoch_num, avg_train_loss)
        
        # Save best model if this epoch is best
        if is_best:
            # Save best model with special naming in run directory
            best_checkpoint_path = os.path.join(trainer.checkpoints_dir, f'best_model_epoch_{epoch_num}.pt')
            torch.save({
                'epoch': epoch_num,
                'model_state_dict': distinanet.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss,
                'val_dist_loss': avg_val_dist,  # Add distance loss to checkpoint
                'val_map': val_map,
                'val_mae': val_mae,
                'config_dict': {
                    'depth': config.depth,
                    'distance_head_type': config.distance_head_type,
                    'distance_loss_type': config.distance_loss_type,
                    'distance_weight': config.distance_weight
                }
            }, best_checkpoint_path)
            tqdm.write(f"⭐ New best model saved! Epoch {epoch_num}, Val Dist Loss: {avg_val_dist:.4f}")
        
        # Update epoch progress bar with comprehensive metrics (focus on distance loss)
        if dataloader_val is not None:
            epoch_pbar.set_postfix({
                'T_Loss': f'{avg_train_loss:.4f}',
                'V_Loss': f'{avg_val_loss:.4f}',
                'V_Dist': f'{avg_val_dist:.4f}',
                'Best_Dist': f'{best_val_dist_loss:.4f}',
                'Time': f'{epoch_time:.1f}s'
            })
        else:
            epoch_pbar.set_postfix({
                'T_Loss': f'{avg_train_loss:.4f}',
                'Time': f'{epoch_time:.1f}s',
                'LR': f'{optimizer.param_groups[0]["lr"]:.2e}'
            })
        
        # 📊 EPOCH COMPLETION STATISTICS
        epoch_stats = f"""
📊 Epoch {epoch_num + 1}/{config.epochs} Complete - Duration: {epoch_time:.2f}s
   Training   → Loss: {avg_train_loss:.6f} | Cls: {avg_train_cls:.6f} | Reg: {avg_train_reg:.6f} | Dist: {avg_train_dist:.6f}"""
        
        if dataloader_val is not None:
            epoch_stats += f"""
   Validation → Loss: {avg_val_loss:.6f} | Cls: {avg_val_cls:.6f} | Reg: {avg_val_reg:.6f} | Dist: {avg_val_dist:.6f}
   Metrics    → mAP: {val_map:.6f} | MAE: {val_mae:.6f} | Best Dist Loss: {best_val_dist_loss:.6f} (Epoch {best_epoch + 1})"""
            
            if is_best:
                epoch_stats += f"""
   🎯 New Best Model! Distance Loss improved from {best_val_dist_loss:.6f} to {avg_val_dist:.6f}"""
        
        tqdm.write(epoch_stats)
        
    
    # Close epoch progress bar
    epoch_pbar.close()

    # Training completed
    total_time = time.time() - training_start_time
    logger.info(f"Training completed in {total_time:.2f}s")
    
    # 🎉 COMPREHENSIVE TRAINING COMPLETION STATISTICS
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = total_time % 60
    
    completion_stats = f"""
🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉

⏱️  TIMING STATISTICS
    Total Training Time: {hours:02d}h:{minutes:02d}m:{seconds:05.2f}s
    Average Time per Epoch: {total_time/config.epochs:.2f}s
    Total Iterations: {config.epochs * len(dataloader_train)}
    Average Iterations per Second: {(config.epochs * len(dataloader_train))/total_time:.2f}

📊 FINAL METRICS"""
    
    if dataloader_val is not None:
        completion_stats += f"""
    � Best Model Performance:
       ├─ Best Distance Loss: {best_val_dist_loss:.6f} (Primary criteria)
       ├─ Best Validation mAP: {best_val_map:.6f}
       ├─ Best Model Epoch: {best_epoch}/{config.epochs}
       └─ Best Model Path: checkpoints/best_model_epoch_{best_epoch}.pt
    
    📈 Final Epoch Results:
       ├─ Training Loss: {avg_train_loss:.6f}
       ├─ Validation Loss: {avg_val_loss:.6f}
       ├─ Validation Distance Loss: {avg_val_dist:.6f}
       └─ Improvement: {((best_val_dist_loss - avg_val_dist)/best_val_dist_loss*100):+.2f}% from best"""
    else:
        completion_stats += f"""
    📈 Final Training Results:
       └─ Final Training Loss: {avg_train_loss:.6f}"""
    
    completion_stats += f"""

💾 SAVED MODELS
    ├─ Run Directory: {run_dir}
    ├─ Latest Model: {os.path.join(trainer.checkpoints_dir, f'epoch_{config.epochs - 1}.pt')}"""
    
    if dataloader_val is not None:
        completion_stats += f"""
    └─ Best Model: {os.path.join(trainer.checkpoints_dir, f'best_model_epoch_{best_epoch}.pt')} (Distance Loss: {best_val_dist_loss:.6f})"""
    
    completion_stats += f"""

📊 OUTPUTS ORGANIZED IN
    ├─ 📁 {run_dir}/
    │   ├─ logs/         (TensorBoard: tensorboard --logdir {os.path.join(run_dir, 'logs')})
    │   ├─ checkpoints/  (Model checkpoints)
    │   └─ test/         (Test results - for future use)

🔧 TRAINING CONFIGURATION
    ├─ Model Depth: {config.depth}
    ├─ Distance Head: {config.distance_head_type}
    ├─ Distance Loss: {config.distance_loss_type}
    ├─ Distance Weight: {config.distance_weight}
    ├─ Batch Size: {config.batch_size}
    ├─ Learning Rate: {config.lr}
    ├─ Optimizer: {config.optimizer}
    └─ Device: {config.device}

🚀 Ready for inference or evaluation!
"""
    
    tqdm.write(completion_stats)
    
    # Save final checkpoint
    trainer.save_checkpoint(distinanet, optimizer, config.epochs - 1, avg_train_loss)
    
    # Cleanup
    trainer.cleanup()
    logger.info("Training finished successfully!")

if __name__ == '__main__':
    # Set multiprocessing start method for CUDA compatibility
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass
    main()
