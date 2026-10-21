
from functools import lru_cache
from pathlib import Path

import torch
from torch.utils.data import DataLoader, SubsetRandomSampler
from torchvision import datasets, transforms


@lru_cache(maxsize=2)
def get_train_dataset(data_name):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])

    root = Path(__file__).resolve().parent / "data"

    if data_name == "CIFAR100":
        return datasets.CIFAR100(
            root=str(root),
            train=True,
            download=False,
            transform=transform,
        )

    if data_name == "CIFAR10":
        return datasets.CIFAR10(
            root=str(root),
            train=True,
            download=False,
            transform=transform,
        )

    raise ValueError(f"Unsupported dataset: {data_name}")


def get_data_loader(client_id, data_idx, batch_size, data_name):
    dataset = get_train_dataset(data_name)
    sampler = SubsetRandomSampler(data_idx[client_id])

    return DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=0,
        generator=torch.Generator().manual_seed(42),
    )
