import torch.optim as optim

class OptimizerFactory:
    """Factory for creating optimizers and schedulers."""
    
    _OPTIMIZERS = {
        'adam': optim.Adam,
        'sgd': optim.SGD,
        'rmsprop': optim.RMSprop,
        'adagrad': optim.Adagrad,
        'nadam': lambda p, lr: optim.NAdam(p, lr=lr, betas=(0.9, 0.999), weight_decay=1e-4)
    }
    
    @classmethod
    def create_optimizer(cls, optimizer_name, model_parameters, lr, logger=None):
        """Create optimizer instance."""
        if logger:
            logger.info(f"Selected optimizer: {optimizer_name}")
        
        if optimizer_name not in cls._OPTIMIZERS:
            raise ValueError(f'Unsupported optimizer: {optimizer_name}. Supported: {list(cls._OPTIMIZERS.keys())}')
        
        if optimizer_name == 'sgd':
            return cls._OPTIMIZERS[optimizer_name](model_parameters, lr=lr, momentum=0.5)
        elif optimizer_name == 'nadam':
            return cls._OPTIMIZERS[optimizer_name](model_parameters, lr=lr)
        else:
            return cls._OPTIMIZERS[optimizer_name](model_parameters, lr=lr)
    
    @staticmethod
    def create_scheduler(optimizer, patience=3):
        """Create learning rate scheduler."""
        return optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=patience, verbose=True)