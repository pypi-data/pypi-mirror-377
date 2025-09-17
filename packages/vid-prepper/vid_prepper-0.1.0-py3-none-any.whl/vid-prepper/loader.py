import subprocess
import torch
import numpy as np
import webdataset as wds
from pathlib import Path
from io import BytesIO
import av
from typing import List, Tuple, Union, Iterator

class VideoLoader:
    def __init__(self, num_frames: int = 16, frame_stride: int = 2, size: Tuple[int, int] = (224, 224), device: str = "cpu", use_nvdec: bool = True) -> None:
        """
        Args:
            num_frames: number of frames to sample per clip
            frame_stride: spacing between sampled frames
            size: (H, W) to resize each frame
            device: "cpu" or "cuda"
            use_nvdec: whether to use FFmpeg + NVDEC if device=='cuda'
        """
        self.num_frames = num_frames
        self.frame_stride = frame_stride
        self.size = size
        self.device = device
        self.use_nvdec = use_nvdec and device=="cuda"

    def _decode_nvdec(self, filepath: Union[str, Path]) -> torch.Tensor:
        """Decode a video file using FFmpeg + NVDEC directly to GPU tensor.
        
        Args:
            filepath: path to the video file

        Returns:
            tensor: video tensor
        """
        H, W = self.size
        cmd = [
            "ffmpeg",
            "-hwaccel", "cuda",
            "-c:v", "h264_cuvid",  # or hevc_cuvid for HEVC
            "-i", str(filepath),
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "pipe:1"
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw = proc.stdout.read()
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("NVDEC decoding failed")
        
        num_frames = len(raw) // (3 * H * W)
        frames = np.frombuffer(raw, np.uint8).reshape(num_frames, H, W, 3)
        tensor = torch.from_numpy(frames).permute(0,3,1,2).float() / 255.0
        if self.device=="cuda":
            tensor = tensor.cuda(non_blocking=True)
        return tensor

    def _decode_pyav(self, video_bytes: bytes) -> List[np.ndarray]:
        """Decode video bytes using PyAV (CPU).
        
        Args:
            video_bytes: bytes of the video file

        Returns:
            list: list of frames
        """
        container = av.open(BytesIO(video_bytes))
        frames = []
        for frame in container.decode(video=0):
            img = frame.to_ndarray(format='rgb24')
            frames.append(img)
        container.close()
        return frames

    def _sample_and_resize(self, frames: List[np.ndarray]) -> torch.Tensor:
        """Sample frames and resize to target size.
        
        Args:
            frames: list of frames

        Returns:
            tensor: video tensor
        """
        import cv2
        total_frames = len(frames)
        if total_frames==0:
            raise ValueError("Video has zero frames")
        indices = np.linspace(0, total_frames-1, num=self.num_frames*self.frame_stride, dtype=int)[::self.frame_stride]
        
        # Pre-allocate tensor for memory efficiency
        tensor = torch.zeros(self.num_frames, 3, self.size[0], self.size[1], dtype=torch.float32)
        
        # Process frames one at a time and fill tensor directly
        for idx, frame_idx in enumerate(indices):
            resized_frame = cv2.resize(frames[frame_idx], (self.size[1], self.size[0]))
            # Convert to tensor format (H,W,C) -> (C,H,W) and normalize
            frame_tensor = torch.from_numpy(resized_frame).permute(2,0,1).float() / 255.0
            tensor[idx] = frame_tensor
        if self.device=="cuda":
            tensor = tensor.cuda(non_blocking=True)
        return tensor

    def load_file(self, filepath: Union[str, Path]) -> torch.Tensor:
        """Load a video file as a tensor.
        
        Args:
            filepath: path to the video file

        Returns:
            tensor: video tensor
        """
        if self.use_nvdec:
            return self._decode_nvdec(filepath)
        else:
            with open(filepath,"rb") as f:
                video_bytes = f.read()
            frames = self._decode_pyav(video_bytes)
            return self._sample_and_resize(frames)

    def load_bytes(self, video_bytes: bytes) -> torch.Tensor:
        """Load video from raw bytes.
        
        Args:
            video_bytes: bytes of the video file

        Returns:
            tensor: video tensor
        """
        frames = self._decode_pyav(video_bytes)
        return self._sample_and_resize(frames)

    def load_files(self, filepaths: List[Union[str, Path]]) -> torch.Tensor:
        """Load multiple videos into a batch tensor (B, T, C, H, W).
        
        Args:
            filepaths: list of paths to the video files

        Returns:
            tensor: video tensor
        """
        clips = [self.load_file(f) for f in filepaths]
        return torch.stack(clips)

    def load_wds(self, wds_path: str, key: str = "mp4", label: str = "cls") -> wds.WebDataset:
        """Return a WebDataset pipeline yielding (tensor, label).
        
        Args:
            wds_path: path to the WebDataset
            key: key to use for video
            label: label to use for video

        Returns:
            WebDataset: WebDataset pipeline
        """
        def decode_sample(video_bytes, lbl):
            tensor = self.load_bytes(video_bytes)
            return tensor, lbl

        dataset = (
            wds.WebDataset(wds_path)
            .to_tuple(key, label)
            .map_tuple(decode_sample)
        )
        return dataset
