import torch
import torchvision.transforms as transforms
from torch.utils.data import Dataset
import numpy as np


class FakeSemanticSegmentationDataset(Dataset):
    """
    A fake dataset for semantic segmentation testing.
    Creates random images and corresponding segmentation masks.
    """

    def __init__(self, image_size, num_images=10, num_classes=2, transform=None):
        self.image_size = image_size
        self.num_images = num_images
        self.num_classes = num_classes
        self.transform = transform

        # Create fake data
        self.images = []
        self.masks = []

        for _ in range(num_images):
            # Create random image
            if isinstance(image_size, int):
                img = np.random.rand(image_size, image_size, 3).astype(np.float32)
            else:
                img = np.random.rand(image_size[0], image_size[1], 3).astype(np.float32)

            # Create random segmentation mask
            if isinstance(image_size, int):
                mask = np.random.randint(
                    0, num_classes, (image_size, image_size), dtype=np.int64
                )
            else:
                mask = np.random.randint(
                    0, num_classes, (image_size[0], image_size[1]), dtype=np.int64
                )

            self.images.append(img)
            self.masks.append(mask)

    def __len__(self):
        return self.num_images

    def __getitem__(self, idx):
        image = self.images[idx]
        mask = self.masks[idx]

        if self.transform:
            image = self.transform(image)
            # For masks, we don't apply the same transforms as they are labels
            mask = torch.from_numpy(mask)
        else:
            # Default transform to tensor
            image = torch.from_numpy(image).permute(2, 0, 1)  # HWC to CHW
            mask = torch.from_numpy(mask)

        return image, mask
