import torch
import numpy as np
import random
from ultralytics import YOLO
import scenedetect
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from typing import List, Optional, Dict, Any, Union

class VideoDetector:
    """
    Video analysis class for shots, wipes, object/person detection using YOLOv8.
    Works efficiently with video tensors or video files.

    Args:
        loader: VideoLoader instance
        device: device to use for detection
        yolov8_model: path to YOLOv8 model
    """

    def __init__(self, loader: Optional[Any] = None, device: str = "cuda", yolov8_model: str = "yolov8n.pt") -> None:
        self.loader = loader
        self.device = device
        self.yolo_model = self._load_yolo_model(yolov8_model, device)

    def _load_yolo_model(self, model_path: str, device: str) -> YOLO:
        model = YOLO(model_path)
        model.to(device)
        return model

    # ---------------- Shot detection ----------------
    def detect_shots(self, video_path: str, method: str = "content") -> List[int]:
        """
        Returns a list of shot start frames for the given video file.

        Args:
            video_path: path to the video file
            method: method to use for shot detection

        Returns:
            list: list of shot start frames
        """
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        # Return start frames
        return [start.frame_num for start, end in scene_list]

    # ---------------- Wipe detection ----------------
    def detect_wipes(self, video_tensor: torch.Tensor, block_grid: Tuple[int, int] = (8, 8), threshold: float = 0.3) -> List[int]:
        """
        Detect wipe transitions based on block color differences.
        Returns a list of frame indices where wipes occur.

        Args:
            video_tensor: video tensor
            block_grid: block grid for detection
            threshold: threshold for detection

        Returns:
            list: list of frame indices where wipes occur
        """
        x = video_tensor.float() / 255.0
        if x.dim() == 5:
            B, T, C, H, W = x.shape
            x = x.view(-1, C, H, W)
        else:
            T, C, H, W = x.shape
            B = 1

        h_blocks, w_blocks = block_grid
        h_size = H // h_blocks
        w_size = W // w_blocks

        block_means = x.unfold(2,h_size,h_size).unfold(3,w_size,w_size).mean(dim=(-1,-2,-3))
        diffs = (block_means[1:] - block_means[:-1]).abs().mean(dim=1)
        wipe_frames = (diffs > threshold).nonzero(as_tuple=True)[0].tolist()
        return wipe_frames

    # ---------------- Object/Person detection ----------------
    def detect_objects(self, video_tensor: torch.Tensor, classes: Optional[List[str]] = None, conf_thresh: float = 0.3) -> List[List[Dict[str, Any]]]:
        """
        Detect objects/persons using YOLOv8.
        Returns nested list: results[clip_idx][frame_idx] = dict with
        'boxes', 'scores', 'labels' (numeric), 'names' (human-readable)

        Args:
            video_tensor: video tensor
            classes: classes to detect
            conf_thresh: confidence threshold

        Returns:
            list: list of results
        """
        if video_tensor.dim() == 5:  # B,T,C,H,W
            B, T, C, H, W = video_tensor.shape
            x = video_tensor.view(-1, C, H, W).to(self.device)
        else:  # single clip T,C,H,W
            B = 1
            T, C, H, W = video_tensor.shape
            x = video_tensor.view(-1, C, H, W).to(self.device)

        # Run YOLOv8 inference
        preds = self.yolo_model(x)

        # Process results
        flat_results = []
        for p in preds:
            boxes = p.boxes.xyxy.cpu().numpy()
            scores = p.boxes.conf.cpu().numpy()
            labels = p.boxes.cls.cpu().numpy().astype(int)
            names = [self.yolo_model.names[i] for i in labels]

            mask = scores >= conf_thresh
            flat_results.append({
                "boxes": boxes[mask],
                "scores": scores[mask],
                "labels": labels[mask],
                "names": np.array(names)[mask].tolist()
            })

        # Reshape results to (B,T)
        if B > 1:
            results = [flat_results[i*T:(i+1)*T] for i in range(B)]
        else:
            results = flat_results
        return results
