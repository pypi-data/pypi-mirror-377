import subprocess
import shutil
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import webdataset as wds
from typing import List, Union


class VideoStandardizer:
    """Standardize videos for deep learning models."""
    def __init__(
        self,
        size: str = "224x224",
        fps: int = 25,
        codec: str = "h264",
        color: str = "rgb",
        use_gpu: bool = True
    ) -> None:
        self.size = size
        self.fps = fps
        self.codec = codec
        self.color = color
        self.use_gpu = use_gpu

        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg not found in PATH")

    def _ffmpeg_cmd(self, input_arg: str, output_path: str) -> List[str]:
        """Build FFmpeg command for direct file output."""
        filters = [f"fps={self.fps}", f"scale={self.size}"]
        filters.append("format=gray" if self.color == "gray" else "format=rgb24")
        vf_filter = ",".join(filters)

        codec = self.codec
        gpu_args = []
        if self.use_gpu and codec in ["h264", "hevc"]:
            codec = f"{codec}_nvenc"
            gpu_args = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]

        cmd = [
            "ffmpeg", "-y",
            "-i", input_arg,
            *gpu_args,
            "-vf", vf_filter,
            "-c:v", codec,
            "-r", str(self.fps),
            str(output_path)
        ]
        return cmd

    def standardize_video(
        self,
        video_input: Union[str, Path],
        output_path: Union[str, Path] = None
    ) -> Path:
        """Standardize a video file and write directly to disk.

        Args:
            video_input: path to input video
            output_path: optional output path; defaults to 'standardized_<input>.mp4'

        Returns:
            Path: path to the standardized video
        """
        video_input = Path(video_input)
        if output_path is None:
            output_path = video_input.parent / f"standardized_{video_input.name}"
        else:
            output_path = Path(output_path)

        cmd = self._ffmpeg_cmd(str(video_input), str(output_path))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = proc.communicate()

        if proc.returncode != 0:
            print(err.decode())
            raise RuntimeError("ffmpeg failed")

        if not output_path.exists():
            raise RuntimeError("ffmpeg did not produce output")

        return output_path

    def batch_standardize(self, videos: List[Union[str, Path]], output_dir: Union[str, Path]) -> List[str]:
        """Standardize multiple videos and save outputs."""
        os.makedirs(output_dir, exist_ok=True)
        results = []

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
            futures = {
                ex.submit(
                    self._process_and_write,
                    vid,
                    Path(output_dir) / Path(vid).name
                ): vid for vid in videos
            }

            for f in as_completed(futures):
                try:
                    results.append(f.result())
                except Exception as e:
                    results.append(f"fail: {e}")
        return results

    def _process_and_write(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> str:
        self.standardize_video(input_path, output_path)
        return f"ok: {output_path}"

    def standardize_wds(self, wds_path: str, key: str = "mp4", label: str = "cls") -> wds.WebDataset:
        """Standardize videos inside a WebDataset."""
        dataset = (
            wds.WebDataset(wds_path)
            .to_tuple(key, label)
            .map_tuple(lambda vid, lbl: (self.standardize_video(vid), lbl))
        )
        return dataset
