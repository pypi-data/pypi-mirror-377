import subprocess
import shutil
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import webdataset as wds
from typing import List, Union, Tuple


class VideoStandardizer:
    """Standardize videos for deep learning models."""
    def __init__(self, size: str = "224x224", fps: int = 25, codec: str = "h264", color: str = "rgb", use_gpu: bool = True) -> None:
        """
        Initialize the VideoStandardizer.
        
        Args:
            size: size of the video
            fps: frames per second
            codec: codec to use
            color: color space
            use_gpu: whether to use GPU acceleration
        """
        self.size = size
        self.fps = fps
        self.codec = codec
        self.color = color
        self.use_gpu = use_gpu

        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg not found in PATH")

    def _ffmpeg_cmd(self, input_arg: str, is_pipe: bool = False) -> List[str]:
        """Build ffmpeg command.
        
        Args:
            input_arg: input file path or pipe
            is_pipe: whether input is a pipe

        Returns:
            list: ffmpeg command
        """
        filters = [f"fps={self.fps}", f"scale={self.size}"]
        if self.color == "gray":
            filters.append("format=gray")
        else:
            filters.append("format=rgb24")
        vf_filter = ",".join(filters)

        codec = self.codec
        gpu_args = []
        if self.use_gpu and codec in ["h264", "hevc"]:
            codec = f"{codec}_nvenc"
            gpu_args = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]

        cmd = [
            "ffmpeg", "-y",
            "-i", input_arg if not is_pipe else "pipe:0",
            *gpu_args,
            "-vf", vf_filter,
            "-c:v", codec,
            "-r", str(self.fps),
            "-f", "mp4", "pipe:1"
        ]
        return cmd

    def standardize_video(self, video_input: Union[str, Path, bytes, bytearray]) -> bytes:
        """Standardize a single video (filepath or bytes) → returns bytes.
        
        Args:
            video_input: input video file path or bytes

        Returns:
            bytes: standardized video
        """
        if isinstance(video_input, (str, Path)):
            cmd = self._ffmpeg_cmd(str(video_input), is_pipe=False)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            out, _ = proc.communicate()
        elif isinstance(video_input, (bytes, bytearray)):
            cmd = self._ffmpeg_cmd("pipe:0", is_pipe=True)
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            out, _ = proc.communicate(input=video_input)
        else:
            raise TypeError("video_input must be filepath (str/Path) or bytes")

        if proc.returncode != 0:
            raise RuntimeError("ffmpeg failed")
        return out

    def batch_standardize(self, videos: List[Union[str, Path]], out_dir: Union[str, Path]) -> List[str]:
        """Standardize a list of filepaths and write outputs.
        
        Args:
            videos: list of input video file paths
            out_dir: output directory

        Returns:
            list: results of processing
        """
        os.makedirs(out_dir, exist_ok=True)
        futures, results = [], []

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
            for vid in videos:
                out_path = Path(out_dir) / Path(vid).name
                futures.append(
                    ex.submit(self._process_and_write, vid, out_path)
                )
            for f in as_completed(futures):
                try:
                    results.append(f.result())
                except Exception as e:
                    results.append(f"fail: {e}")
        return results

    def _process_and_write(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> str:
        """Helper for batch processing.
        
        Args:
            input_path: input video file path
            output_path: output video file path

        Returns:
            str: result of processing
        """
        out_bytes = self.standardize_video(str(input_path))
        with open(output_path, "wb") as f:
            f.write(out_bytes)
        return f"ok: {output_path}"

    def standardize_wds(self, wds_path: str, key: str = "mp4", label: str = "cls") -> wds.WebDataset:
        """
        Return a WebDataset pipeline where each video is standardized.
        
        Args:
            wds_path: input WebDataset path
            key: key to use for video
            label: label to use for video

        Returns:
            WebDataset: standardized WebDataset
        """
        dataset = (
            wds.WebDataset(wds_path)
            .to_tuple(key, label)
            .map_tuple(lambda vid, lbl: (self.standardize_video(vid), lbl))
        )
        return dataset
