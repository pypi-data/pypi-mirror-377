import torch
import numpy as np
from typing import List, Optional, Dict, Any, Tuple

from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

import scenedetect
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


class VideoDetector:
    """
    Video analysis class for shots, wipes, and zero-shot object detection
    using GroundingDINO (IDEA-Research/grounding-dino-tiny).
    Defaults to subsection of COCO classes if no text query is provided.
    """

    def __init__(
        self,
        loader: Optional[Any] = None,
        device: str = "cuda",
        model_id: str = "IDEA-Research/grounding-dino-tiny",
    ) -> None:
        self.loader = loader
        self.device = device
        self.model_id = model_id
        self.MAIN_COCO_CLASSES = [
                                    "person",
                                    "car",
                                    "truck",
                                    "bus",
                                    "bicycle",
                                    "motorcycle",
                                    "train",
                                    "airplane",
                                    "dog",
                                    "cat",
                                    "bird",
                                    "horse",
                                    "sheep",
                                    "cow",
                                    "elephant",
                                    "zebra",
                                    "giraffe",
                                    "backpack",
                                    "handbag",
                                    "suitcase"
                                ]

    # ---------------- Shot detection ----------------
    def detect_shots(self, video_path: str, method: str = "content") -> List[int]:
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        return [start.frame_num for start, end in scene_list]

    # ---------------- Wipe detection ----------------
    def detect_wipes(
        self,
        video_tensor: torch.Tensor,
        block_grid: Tuple[int, int] = (8, 8),
        threshold: float = 0.3,
    ) -> List[int]:
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

        block_means = (
            x.unfold(2, h_size, h_size)
            .unfold(3, w_size, w_size)
            .mean(dim=(-1, -2, -3))
        )
        diffs = (block_means[1:] - block_means[:-1]).abs().mean(dim=1)
        wipe_frames = (diffs > threshold).nonzero(as_tuple=True)[0].tolist()
        return wipe_frames

    # ---------------- Object/Person detection ----------------
    def detect_objects(
        self,
        video_tensor: torch.Tensor,
        text_queries: Optional[str] = None,
        text_threshold: float = 0.3,
    ) -> List[List[Dict[str, Any]]]:
        """
        Zero-shot object detection using text queries.
        If no text_queries is provided, defaults to all 80 COCO categories.

        Args:
            video_tensor: video tensor [B,T,C,H,W] or [T,C,H,W]
            text_queries: string like "a cat. a dog."
                          (must be lowercase, queries end with '.')
            text_threshold: min confidence for text match
        """
        processor = AutoProcessor.from_pretrained(self.model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id).to(self.device)
        
        if text_queries is None:
            text_queries = " ".join(f"a {cls}." for cls in self.MAIN_COCO_CLASSES)

        if video_tensor.dim() == 5:  # B,T,C,H,W
            B, T, C, H, W = video_tensor.shape
            x = video_tensor.view(-1, C, H, W)
        else:  # single clip T,C,H,W
            B = 1
            T, C, H, W = video_tensor.shape
            x = video_tensor.view(-1, C, H, W)

        results = []
        for frame in x:
            image = Image.fromarray((frame.permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8))

            inputs = processor(images=image, text=text_queries, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = model(**inputs)

            postprocessed = processor.post_process_grounded_object_detection(
                outputs,
                inputs.input_ids,
                text_threshold=text_threshold,
                target_sizes=[image.size[::-1]],
            )[0]

            # Map token indices back to COCO class names
            boxes = postprocessed["boxes"].cpu().numpy()
            scores = postprocessed["scores"].cpu().numpy()
            labels = postprocessed["labels"]

            results.append(
                {
                    "boxes": boxes,
                    "scores": scores,
                    "labels": labels
                }
            )

        if B > 1:
            results = [results[i * T : (i + 1) * T] for i in range(B)]

        return results
