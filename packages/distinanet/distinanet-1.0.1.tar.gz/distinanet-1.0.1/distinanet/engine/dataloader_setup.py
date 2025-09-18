import torch
from torchvision import transforms
from torch.utils.data import DataLoader
from distinanet.data.datasets import CSVDataset
from distinanet.data.collater import Collater
from distinanet.data.transforms import Resizer, Augmenter, Normalizer
from distinanet.data.samplers import AspectRatioBasedSampler

def get_training_dataloaders(args, logger):
    """
    Creates and returns the training and validation dataloaders.
    """
    logger.info("Setting up data loaders...")
    
    # Training dataset
    dataset_train = CSVDataset(
        train_file=args.csv_train,
        class_list=args.csv_classes,
        transform=transforms.Compose([Normalizer(), Augmenter(), Resizer()]),
        device=args.device
    )

    sampler = AspectRatioBasedSampler(dataset_train, batch_size=args.batch_size, drop_last=False)
    dataloader_train = DataLoader(dataset_train, num_workers=1, collate_fn=Collater(), batch_sampler=sampler)

    # Validation dataset
    if args.csv_val is None:
        logger.error('No validation annotations provided.')
        raise ValueError('Validation annotations are required for training.')
    
    device_val = torch.device("cpu")
    dataset_val = CSVDataset(
        train_file=args.csv_val,
        class_list=args.csv_classes,
        transform=transforms.Compose([Normalizer(), Resizer()]),
        device=device_val
    )
    
    sampler_val = AspectRatioBasedSampler(dataset_val, batch_size=args.batch_size, drop_last=False)
    dataloader_val = DataLoader(dataset_val, num_workers=5, collate_fn=Collater(), batch_sampler=sampler_val)

    logger.info("Data loaders created successfully.")
    return dataloader_train, dataloader_val, dataset_train, dataset_val
