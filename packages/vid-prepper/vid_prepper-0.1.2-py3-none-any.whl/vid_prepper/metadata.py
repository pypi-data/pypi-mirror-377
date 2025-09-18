import subprocess
import json
from pathlib import Path
from typing import List, Callable, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed


class MetadataError(Exception):
    """Custom exception for ffprobe failures."""
    pass


class Metadata:
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path = Path(file_path)
        self._metadata = None
        self.errors: list[dict] = []

    # ------------------------------
    # Core runner
    # ------------------------------
    def run(self) -> Dict[str, Any]:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-print_format", "json",
            str(self.file_path),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self._metadata = json.loads(result.stdout)
            return self._metadata
        except subprocess.CalledProcessError as e:
            raise MetadataError(f"ffprobe failed: {e.stderr.strip()}") from e
        except json.JSONDecodeError:
            raise MetadataError("Failed to parse ffprobe output as JSON")

    @property
    def metadata(self) -> Dict[str, Any]:
        if self._metadata is None:
            raise MetadataError("FFProbe has not been run yet")
        return self._metadata

    # ------------------------------
    # Error logging
    # ------------------------------
    def _log_error(self, check: str, message: str) -> None:
        self.errors.append({
            "file": str(self.file_path),
            "check": check,
            "message": message
        })

    def export_errors(self, as_json: bool = True) -> Union[str, List[Dict[str, str]]]:
        return json.dumps(self.errors, indent=2) if as_json else self.errors

    # ------------------------------
    # Filters
    # ------------------------------
    def filter_missing_video(self) -> bool:
        ok = any(s.get("codec_type") == "video" for s in self.metadata.get("streams", []))
        if not ok:
            self._log_error("missing_video", "No video stream found")
        return ok

    def filter_missing_audio(self) -> bool:
        ok = any(s.get("codec_type") == "audio" for s in self.metadata.get("streams", []))
        if not ok:
            self._log_error("missing_audio", "No audio stream found")
        return ok

    def filter_variable_framerate(self) -> bool:
        for s in self.metadata.get("streams", []):
            if s.get("codec_type") == "video":
                if s.get("avg_frame_rate") != s.get("r_frame_rate"):
                    self._log_error("variable_framerate", "Framerate is variable")
                    return False
        return True

    def filter_resolution(self, min_width: int = 320, min_height: int = 240) -> bool:
        for s in self.metadata.get("streams", []):
            if s.get("codec_type") == "video":
                w, h = s.get("width"), s.get("height")
                if not w or not h or w < min_width or h < min_height:
                    self._log_error("resolution", f"Resolution too low: {w}x{h}")
                    return False
        return True

    def filter_duration(self, min_seconds: float = 1.0) -> bool:
        try:
            dur = float(self.metadata["format"]["duration"])
            if dur < min_seconds:
                self._log_error("duration", f"Duration too short: {dur:.2f}s")
                return False
            return True
        except Exception:
            self._log_error("duration", "Missing or invalid duration")
            return False

    def filter_pixel_format(self, allowed: Optional[List[str]] = None) -> bool:
        if allowed is None:
            allowed = ["yuv420p"]
        for s in self.metadata.get("streams", []):
            if s.get("codec_type") == "video":
                pix_fmt = s.get("pix_fmt")
                if pix_fmt not in allowed:
                    self._log_error("pixel_format", f"Pixel format {pix_fmt} not allowed")
                    return False
        return True

    def filter_codecs(self, allowed: Optional[List[str]] = None) -> bool:
        if allowed is None:
            allowed = ["h264", "hevc", "vp9"]
        for s in self.metadata.get("streams", []):
            if s.get("codec_type") == "video":
                codec = s.get("codec_name")
                if codec not in allowed:
                    self._log_error("codec", f"Codec {codec} not allowed")
                    return False
        return True


    # ------------------------------
    # Batch validator
    # ------------------------------
    @staticmethod
    def validate_videos(
        inputs: List[str],
        filters: Optional[List[str]] = None,
        max_workers: int = 4,
        only_errors: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Run selected filters on a batch of videos and return metadata + error report.

        Args:
            inputs: list of video file paths
            filters: list of filter method names (defaults to all)
            max_workers: number of threads for parallel execution
            only_errors: if True, return only files with errors (errors only, no metadata)

        Returns:
            List of dicts:
              - if only_errors=False: {"file", "metadata", "errors"}
              - if only_errors=True: {"file", "errors"}
        """
        if filters is None:
            filters = [
                "filter_missing_video",
                "filter_missing_audio",
                "filter_variable_framerate",
                "filter_resolution",
                "filter_duration",
                "filter_pixel_format",
                "filter_codecs",
            ]

        results: list[dict] = []

        def worker(path: str) -> dict:
            probe = Metadata(path)
            metadata = None
            try:
                metadata = probe.run()
                for fname in filters:
                    method: Callable = getattr(probe, fname)
                    method()  # logs errors internally
            except Exception as e:
                probe._log_error("ffprobe_run", str(e))

            if only_errors:
                return {"file": str(path), "errors": probe.errors}
            else:
                return {"file": str(path), "metadata": metadata, "errors": probe.errors}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker, p) for p in inputs]
            for f in as_completed(futures):
                results.append(f.result())

        if only_errors:
            results = [r for r in results if r["errors"]]

        return results
