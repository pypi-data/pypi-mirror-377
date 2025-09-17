"""Extract features from images with AnyDorsal.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

Typical usage example:

  foo = ClassFoo()
  bar = foo.function_bar()
"""
from typing import Optional, Dict, LiteralString
import os

from sklearn.preprocessing import normalize
from torch import nn
from torch.amp import autocast # pyright: ignore[reportPrivateImportUsage] 
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import v2
from torchvision.io import decode_image
from tqdm import tqdm

import numpy as np
import pandas as pd
import timm
import torch
import torch.nn.functional as F
import torch.utils.checkpoint as cp

# def main():

#     # Print the name of the device
#     if torch.cuda.is_available():
#         print('... with cuda device:', torch.cuda.get_device_name())
#         mem = torch.cuda.get_device_properties(0).total_memory
#         print('... which has', int(mem / 1024**3), 'GB of memory')

#     # sometimes I want to up the batch size depending on which GPU i get
#     user_input = input('Continue? (y/n): ')
#     if user_input.lower() != 'y':
#         print('Exiting...')
#         return
    
#     # Load the configuration file
#     with open('config.yaml', 'r') as f:
#         config = yaml.load(f, Loader=yaml.SafeLoader)

#     # create an output directory
#     root = config['image_root']
#     out_dir = os.path.join(root, 'features')
#     os.makedirs(out_dir, exist_ok=True)

#     # extract the features
#     sample_size = config['sample_size']
#     for sample in range(sample_size):
#         print('Sample:', sample)
#         features = extract(config)

#         # define the output path
#         if config['stochastic']:
#             out_path = os.path.join(out_dir, f'features_{sample:>03}.npy')
#         else:
#             out_path = os.path.join(out_dir, 'features.npy')

#         # save the features
#         np.save(out_path, features)

    # # might as well save the features in a single array
    # if config['stochastic']:
    #     stochastic_features = [f for f in os.listdir(out_dir) if 'sample' in f]
    #     files = [k for k in features.keys()]
    #     features_array = load_all_features(stochastic_features, files)
    #     out_path = os.path.join(out_dir, 'stochastic_feature_array.npy')
    #     np.save(out_path, features_array)

def verify_pytorch() -> None:
    """Verify PyTorch installation and show device options."""
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} detected")
        
        # Check all device options
        if torch.cuda.is_available():
            print(f"✓ CUDA GPU available: {torch.cuda.get_device_name(0)}")
        
        if torch.backends.mps.is_available():
            print("✓ Apple Silicon (MPS) GPU available")
        
        if not torch.cuda.is_available() and not torch.backends.mps.is_available():
            print("! No GPU acceleration available. Expect slow feature extraction.")
            
        return None
    
    except ImportError:
        print("✗ PyTorch not found!")
        print("See homepage for PyTorch installation instructions")

        return None
    
def get_best_device() -> LiteralString:
    """Select torch device based on expected performance."""
    if torch.cuda.is_available():
        device = "cuda"
        device_name = torch.cuda.get_device_name(0)
    elif torch.backends.mps.is_available():
        device = "mps"
        device_name = "Apple Silicon GPU"
    else:
        device = "cpu"
        device_name = "CPU"
    
    print(f"Using device: {device} ({device_name})")
    return device

class FeatureExtractor:

    def __init__(self, batch_size: int, model_path: str, 
                 device: Optional[str]=None, 
                 stochastic: bool=False,
                 bbox_csv: Optional[str]=None):
        self.batch_size = batch_size
        self.model_path = model_path
        self.stochastic = stochastic
        self.bbox_csv = bbox_csv
        if device is None:
            self.device = get_best_device()
        else:
            self.device = device

    def extract(self, image_dir: str) -> Dict:

        print('Loading model...')
        model = self.get_model()
        
        if not self.stochastic:
            model.eval()

        test_dataloader = get_test_data(image_dir, self.batch_size, self.bbox_csv)

        print('Extracting features...')
        features = self.extract_features(test_dataloader, model)

        return features
    
    def get_model(self):
        """Build the model from the checkpoint."""
        # Create the backbone
        backbone = EfficientNetCustomBackbone(
            model_name='tf_efficientnet_l2_ns',
            drop_path_rate=0.2,
            with_cp=False
        )
        
        # Create the complete model
        model = ImageClassifier(
            backbone=backbone,
            in_channels=5504,  # Feature dimension for efficientnet_l2_ns
            num_classes=15587  # Number of classes
        )
        
        # Load the checkpoint
        print('Loading model from:', self.model_path, )
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Process state dict
        state_dict = checkpoint["state_dict"]
        if 'head.compute_loss.margins' in state_dict:
            _ = state_dict.pop('head.compute_loss.margins')
        
        # Adapt the state dict keys if needed
        new_state_dict = {}
        for k, v in state_dict.items():
            # Handle backbone keys
            if k.startswith('backbone.timm_model.'):
                # Map to our structure
                if 'blocks' in k:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
                elif 'conv_stem' in k:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
                elif 'bn1' in k:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
                elif 'bn2' in k:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
                elif 'conv_head' in k:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
                else:
                    new_k = k.replace('backbone.timm_model.', 'backbone.base_model.')
            else:
                new_k = k
            new_state_dict[new_k] = v
        
        # Load state dict with some flexibility for missing keys
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
        
        if missing_keys:
            print(f"Warning: Missing keys when loading pretrained weights: {missing_keys}")
        if unexpected_keys:
            print(f"Warning: Unexpected keys when loading pretrained weights: {unexpected_keys}")
        
        # # Convert DropPath to inference mode if stochastic is enabled
        # if stochastic:
        #     model = convert_droppath_to_inference(model)
        
        # Move model to device
        model.to(self.device)
        
        return model

    def extract_features(self, dataloader, model) -> dict:
        """Extract features from images using the model."""
        file_list = []
        feature_list = []

        with torch.no_grad():
            for file, image in tqdm(dataloader):
                image = image.to(self.device)
                with autocast(self.device): # Big speed up
                    feature_vector = model(image, return_loss=False)

                file_list.append(file)
                feature_list.append(feature_vector.cpu().numpy())

        # Handle case with only one batch
        if isinstance(file_list[0], list) or isinstance(file_list[0], tuple):
            files = np.concatenate(file_list)
        else:
            files = np.array(file_list)
            
        feats = np.vstack(feature_list)

        # Create dictionary mapping filenames to features
        feature_dict = dict(zip(files, feats))
        
        return feature_dict

class EfficientNetCustomBackbone(nn.Module):
    """Custom EfficientNet backbone that mimics the MMCLS implementation."""
    def __init__(self, model_name='tf_efficientnet_l2_ns', drop_path_rate=0.2, with_cp=False):
        super().__init__()
        # Create the base model
        self.base_model = timm.create_model(
            model_name,
            pretrained=False,
            drop_path_rate=drop_path_rate,
        )
        self.with_cp = with_cp
        
        # Remove the classifier and pooling 
        self.base_model.classifier = nn.Identity()
        self.base_model.global_pool = nn.Identity()
        
    def forward(self, x):
        # We need to replicate the exact forward pass from your MMCLS TimmEfficientNet class
        # This extracts features before the pooling layer
        
        # Apply stem
        x = self.base_model.conv_stem(x)
        x = self.base_model.bn1(x)
        # x = self.base_model.act1(x)
        
        # Process through all blocks
        for block_idx, blocks in enumerate(self.base_model.blocks):
            for idx, block in enumerate(blocks):
                if self.with_cp and x.requires_grad: # pyright: ignore[reportOptionalMemberAccess]
                    x = cp.checkpoint(block, x)
                else:
                    x = block(x)
        
        # Final convolution and activation
        x = self.base_model.conv_head(x)
        x = self.base_model.bn2(x)
        # x = self.base_model.act2(x)
        
        return x

class NormLinear(nn.Linear):
    """Linear layer with optional feature and weight normalization."""
    def __init__(self, in_features, out_features, bias=False, feature_norm=True, 
                 weight_norm=True):
        super().__init__(in_features, out_features, bias=bias)
        self.weight_norm = weight_norm
        self.feature_norm = feature_norm

    def forward(self, data):
        if self.feature_norm:
            data = F.normalize(data)
        if self.weight_norm:
            weight = F.normalize(self.weight)
        else:
            weight = self.weight
        return F.linear(data, weight, self.bias)


class ImageClassifier(nn.Module):
    """Complete model that mimics the MMCLS classifier structure."""
    def __init__(self, backbone, in_channels=5504, num_classes=15587):
        super().__init__()
        self.backbone = backbone
        
        # Global pooling layer
        self.neck = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classification head
        self.head = NormLinear(
            in_features=in_channels,
            out_features=num_classes,
            bias=False,
            feature_norm=True,
            weight_norm=True
        )
        
    def forward(self, x, return_loss=True):
        # Extract features from backbone
        x = self.backbone(x)
        
        # Apply global pooling and flatten
        x = self.neck(x)
        x = torch.flatten(x, 1)
        
        # Return features if not computing loss
        if not return_loss:
            return F.normalize(x)
        
        # Compute logits for training (not used in feature extraction)
        logits = self.head(x)
        return logits

def load_bounding_boxes(csv_path):
    '''Load bounding boxes from a CSV file.'''
    df = pd.read_csv(csv_path)
    bboxes = {}
    for _, row in df.iterrows():
        # filename = row['image_name']
        # bbox_columns = ['bbox_x', 'bbox_y', 'bbox_width', 'bbox_height']
        # xmin, ymin, w, h = row[bbox_columns].values
        # xmax, ymax = xmin + w, ymin + h
        filename = row['filename']
        xmin, ymin, xmax, ymax = row['xmin'], row['ymin'], row['xmax'], row['ymax']
        bboxes[filename] = (xmin, ymin, xmax, ymax)
    return bboxes

class DorsalImageDataset(Dataset):
    """Dataset for dorsal fin images with optional bounding boxes."""
    def __init__(self, image_dir, transform=None, bbox_csv=None):
        self.image_dir = image_dir
        self.transform = transform
        self.images = list_images(image_dir)
        self.bboxes = load_bounding_boxes(bbox_csv) if bbox_csv else None

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        filename = self.images[idx]
        full_path = os.path.join(self.image_dir, filename)
        image = decode_image(full_path)
        if self.bboxes and filename in self.bboxes:
            bbox = self.bboxes[filename]
            # Crop image to bounding box
            image = image[:, bbox[1]:bbox[3], bbox[0]:bbox[2]]
        if self.transform:
            image = self.transform(image)
        return filename, image
    
def get_test_data(directory, batch_size, bbox_csv=None):
    """Get the dataloader from a directory of images."""
    # RGB normalization values
    bgr_mean = np.array([123.675, 116.28, 103.53]) / 255
    bgr_std = np.array([58.395, 57.12, 57.375]) / 255

    rgb_mean = bgr_mean[[2, 1, 0]]
    rgb_std = bgr_std[[2, 1, 0]]

    image_size = (768, 768)

    data_transforms = v2.Compose([
        v2.Resize(image_size),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(rgb_mean.tolist(), rgb_std.tolist()),
    ])

    test_data = DorsalImageDataset(directory, transform=data_transforms, 
                                  bbox_csv=bbox_csv)
    
    dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, 
                           num_workers=2, pin_memory=True)

    return dataloader
    
def list_images(image_dir):
    """List all images in a directory."""
    images = []
    formats = ('png', 'jpg', 'jpeg')

    for file in os.listdir(image_dir):
        if file.lower().endswith(formats):
            images.append(file)

    return images

def load_and_process_features(path, image_list, l2=True):
    """Load features for a single file and process them into array format."""
    features = np.load(path, allow_pickle=True).item()
    feature_array = np.array([np.array(features[image]) for image in image_list])

    if l2:
        feature_array = normalize(feature_array, axis=0)
        
    return feature_array

def load_all_features(feature_paths, image_list):
    """Load and process all features."""
    feature_list = []
    print('Loading features...')
    for path in tqdm(feature_paths):
        feature = load_and_process_features(path, image_list)
        feature_list.append(feature)
    return np.stack(feature_list, axis=1)