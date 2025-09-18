import torch
import os

class CheckpointManager(object):
    """
    Manages saving and loading of model checkpoints.
    """

    def load_checkpoint(args, model, optimizer, scheduler, logger):
        """
        Loads a checkpoint if specified in the arguments.
        """
        start_epoch = 0
        best_mAP = 0
        best_mae = float('inf')
        best_epoch_mAP = None
        best_epoch_mae = None

        if args.load_checkpoint:
            logger.info(f"Loading checkpoint '{args.load_checkpoint}'")
            checkpoint = torch.load(args.load_checkpoint, map_location=args.device)
            
            model.load_state_dict(checkpoint['model_state'])
            optimizer.load_state_dict(checkpoint['optimizer_state'])

            if 'scheduler_state' in checkpoint and scheduler:
                scheduler.load_state_dict(checkpoint['scheduler_state'])

            start_epoch = checkpoint['epoch'] + 1
            best_mAP = checkpoint.get('best_mAP', 0)
            best_mae = checkpoint.get('best_mae', float('inf'))
            best_epoch_mAP = checkpoint.get('best_epoch_mAP', None)
            best_epoch_mae = checkpoint.get('best_epoch_mae', None)

            logger.info(f"Checkpoint loaded successfully, resuming from epoch {start_epoch}.")
            
        return start_epoch, best_mAP, best_mae, best_epoch_mAP, best_epoch_mae

    def save_checkpoint(epoch, model, optimizer, scheduler, best_mAP, best_mae, best_epoch_mAP, best_epoch_mae, log_dir):
        """
        Saves a training checkpoint.
        """
        model_path = os.path.join(log_dir, 'models')
        os.makedirs(model_path, exist_ok=True)

        state = {
            'epoch': epoch,
            'model_state': model.module.state_dict() if hasattr(model, 'module') else model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'scheduler_state': scheduler.state_dict() if scheduler else None,
            'best_mAP': best_mAP,
            'best_mae': best_mae,
            'best_epoch_mAP': best_epoch_mAP,
            'best_epoch_mae': best_epoch_mae
        }

        torch.save(state, os.path.join(model_path, f'state_{epoch}.pt'))
        torch.save(model.module, os.path.join(model_path, f'checkpoint_{epoch}.pt'))
