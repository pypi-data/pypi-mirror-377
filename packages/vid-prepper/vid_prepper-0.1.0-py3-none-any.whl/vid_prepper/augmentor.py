import torch
import kornia.filters as KF
import kornia.augmentation as K
import torch.nn.functional as F
import random
import numpy as np
from typing import List, Tuple, Union, Dict, Any

class VideoAugmentor:
    """
    Efficient video augmentation class for tensors from VideoLoader.
    Input tensor shapes: (T,C,H,W) or (B,T,C,H,W).
    Each augmentation can be called individually or chained in a sequence.

    Args:
        device: device to use for augmentation
    """

    def __init__(self, device: str = "cuda") -> None:
        self.device = device

    
    def _merge_batch_time(self, videos: torch.Tensor) -> torch.Tensor:
        """Merge batch and time dimensions.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)

        Returns:
            tensor: merged tensor (B*T,C,H,W)
        """
        if videos.dim() == 5:
            B,T,C,H,W = videos.shape
            return videos.view(B*T, C, H, W)
        return videos

    def _unmerge_batch_time(self, x_aug: torch.Tensor, original_shape: Tuple[int, ...]) -> torch.Tensor:
        """Unmerge batch and time dimensions.
        
        Args:
            x_aug: augmented tensor (B*T,C,H,W)
            original_shape: original shape of the tensor (T,C,H,W) or (B,T,C,H,W)

        Returns:
            tensor: unmerged tensor (B,T,C,H,W)
        """
        if len(original_shape) == 5:
            B,T,C,H,W = original_shape
            return x_aug.view(B,T,C,H,W)
        return x_aug

    def _to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move tensor to device if not already on the correct device.
        
        Args:
            tensor: input tensor

        Returns:
            tensor: tensor on the correct device
        """
        if tensor.device != torch.device(self.device):
            return tensor.to(self.device)
        return tensor

    # ---------------- Augmentations ----------------
    def crop(self, videos: torch.Tensor, type: str = "random", size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
        """Crop video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            type: type of crop (random or center)
            size: size of the crop

        Returns:
            tensor: cropped tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        C,H,W = x.shape[1:]
        th, tw = size
        if type=="center":
            i = (H - th)//2
            j = (W - tw)//2
        elif type=="random":
            i = torch.randint(0, H-th+1, (1,)).item()
            j = torch.randint(0, W-tw+1, (1,)).item()
        else:
            raise ValueError("crop type must be 'random' or 'center'")
        x = x[:,:, i:i+th, j:j+tw]
        return self._unmerge_batch_time(x, videos.shape)

    def flip(self, videos: torch.Tensor, type: str = "horizontal") -> torch.Tensor:
        """Flip video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            type: type of flip (horizontal or vertical)

        Returns:
            tensor: flipped tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        if type=="horizontal":
            x = torch.flip(x, dims=[3])
        elif type=="vertical":
            x = torch.flip(x, dims=[2])
        else:
            raise ValueError("flip type must be 'horizontal' or 'vertical'")
        return self._unmerge_batch_time(x, videos.shape)

    def mirror(self, videos: torch.Tensor, edge: str = "upper") -> torch.Tensor:
        """Mirror video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            edge: edge to mirror (upper, lower, left, right)

        Returns:
            tensor: mirrored tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        B,C,H,W = x.shape
        if edge=="upper":
            top = x[:,:,0:H//2,:]
            x[:,:,H//2:,:] = torch.flip(top, dims=[2])
        elif edge=="lower":
            bottom = x[:,:,H//2:,:]
            x[:,:,0:H//2,:] = torch.flip(bottom, dims=[2])
        elif edge=="left":
            left = x[:,:,:,0:W//2]
            x[:,:,:,W//2:] = torch.flip(left,dims=[3])
        elif edge=="right":
            right = x[:,:,:,W//2:]
            x[:,:,:,0:W//2] = torch.flip(right,dims=[3])
        else:
            raise ValueError("mirror edge must be upper/lower/left/right")
        return self._unmerge_batch_time(x, videos.shape)

    def pad(self, videos: torch.Tensor, proportion: Union[str, float] = "10%", fill: float = 0) -> torch.Tensor:
        """Pad video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            proportion: proportion to pad
            fill: fill value

        Returns:
            tensor: padded tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        if isinstance(proportion,str) and proportion.endswith('%'):
            prop = float(proportion.strip('%'))/100
        else:
            prop = float(proportion)
        B,C,H,W = x.shape
        pad_h = int(H*prop)
        pad_w = int(W*prop)
        x = F.pad(x, (pad_w,pad_w,pad_h,pad_h), value=fill)
        return self._unmerge_batch_time(x, videos.shape)

    def gaussian_blur(
        self,
        videos: torch.Tensor,
        kernel_size: int = 5,
        sigma: float = 1.0,
        random: bool = False
    ) -> torch.Tensor:
        """Apply Gaussian blur to video.

        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            kernel_size: size of the Gaussian kernel
            sigma: standard deviation of the Gaussian
            random: if True, use stochastic Kornia augmentation
                    if False, use deterministic Kornia filter

        Returns:
            tensor: blurred tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)

        if random:
            blur = K.RandomGaussianBlur((kernel_size, kernel_size), (sigma, sigma))
        else:
            blur = KF.GaussianBlur2d((kernel_size, kernel_size), (sigma, sigma))

        x = blur(x)
        return self._unmerge_batch_time(x, videos.shape)

    def brightness(self, videos: torch.Tensor, amount: float = 0.2) -> torch.Tensor:
        """Brightness video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            amount: amount of brightness

        Returns:
            tensor: brightened tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        adjust = K.ColorJitter(brightness=amount, contrast=0, saturation=0, hue=0)
        x = adjust(x)
        return self._unmerge_batch_time(x, videos.shape)

    def contrast(self, videos: torch.Tensor, amount: float = 0.2) -> torch.Tensor:
        """Contrast video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            amount: amount of contrast

        Returns:
            tensor: contrasted tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        adjust = K.ColorJitter(brightness=0, contrast=amount, saturation=0, hue=0)
        x = adjust(x)
        return self._unmerge_batch_time(x, videos.shape)

    def saturation(self, videos: torch.Tensor, amount: float = 0.2) -> torch.Tensor:
        """Saturation video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            amount: amount of saturation

        Returns:
            tensor: saturated tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        adjust = K.ColorJitter(brightness=0, contrast=0, saturation=amount, hue=0)
        x = adjust(x)
        return self._unmerge_batch_time(x, videos.shape)

    def color_adjust(self, videos: torch.Tensor, red: float = 1.0, green: float = 1.0, blue: float = 1.0) -> torch.Tensor:
        """Color adjust video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            red: amount of red
            green: amount of green
            blue: amount of blue

        Returns:
            tensor: color adjusted tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        x[:,0,:,:] = x[:,0,:,:]*red
        x[:,1,:,:] = x[:,1,:,:]*green
        x[:,2,:,:] = x[:,2,:,:]*blue
        return self._unmerge_batch_time(x, videos.shape)

    def coarse_dropout(self, videos: torch.Tensor, number_holes_range: List[int] = [1, 5],
                       hole_width_range: List[int] = [10, 50], hole_height_range: List[int] = [10, 50], fill: float = 0) -> torch.Tensor:
        """Coarse dropout video.
        
        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            number_holes_range: range of number of holes
            hole_width_range: range of width of holes
            hole_height_range: range of height of holes
            fill: fill value

        Returns:
            tensor: coarse dropout tensor
        """
        x = self._merge_batch_time(videos)
        x = self._to_device(x)
        B,C,H,W = x.shape
        num_holes = random.randint(*number_holes_range)
        
        # Generate all random numbers at once for efficiency
        hole_heights = np.random.randint(*hole_height_range, size=num_holes)
        hole_widths = np.random.randint(*hole_width_range, size=num_holes)
        y_positions = np.random.randint(0, H - hole_heights.max() + 1, size=num_holes)
        x_positions = np.random.randint(0, W - hole_widths.max() + 1, size=num_holes)
        
        # Apply dropout holes
        for i in range(num_holes):
            hh, hw = hole_heights[i], hole_widths[i]
            y, x_pos = y_positions[i], x_positions[i]
            # Ensure hole fits within bounds
            y_end = min(y + hh, H)
            x_end = min(x_pos + hw, W)
            x[:,:,y:y_end,x_pos:x_end] = fill
        return self._unmerge_batch_time(x, videos.shape)

    # ---------------- Chain multiple augmentations ----------------
    def chain(self, videos: torch.Tensor, augmentations: List[Tuple[str, Dict[str, Any]]]) -> torch.Tensor:
        """
        Apply a sequence of augmentations.

        Args:
            videos: input tensor (T,C,H,W) or (B,T,C,H,W)
            augmentations: list of tuples (method_name, kwargs_dict)

        Example:
            augmentor.chain(videos, [
                ('crop', {'type': 'random', 'size': (200, 200)}),
                ('flip', {'type': 'horizontal'}),
                ('gaussian_blur', {'kernel_size': 7, 'sigma': 2.0, 'random': True}),
                ('brightness', {'amount': 0.3}),
            ])
        """
        out = videos
        for aug_name, kwargs in augmentations:
            if not hasattr(self, aug_name):
                raise ValueError(f"Unknown augmentation {aug_name}")
            method = getattr(self, aug_name)
            out = method(out, **kwargs)
        return out

