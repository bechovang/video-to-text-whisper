#!/usr/bin/env python3
"""
OBS Video → Transcript Tool
Convert video files to text transcripts using OpenAI Whisper API
"""

import os
import sys
import argparse
import subprocess
import shutil
import uuid
from pathlib import Path
from typing import Optional, List, Tuple

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package. Run: pip install -r requirements.txt")
    print(f"Details: {e}")
    sys.exit(1)

# Load environment variables (override system env with .env file values)
load_dotenv(override=True)


class Config:
    """Configuration management"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "vi")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "")
    KEEP_MP3 = os.getenv("KEEP_MP3", "false").lower() == "true"


class VideoConverter:
    """Convert video files to MP3 using FFmpeg"""

    # MP3 excluded here — handled separately to force re-encode
    SUPPORTED_FORMATS = {".mkv", ".mp4", ".mov", ".flv", ".avi", ".webm", ".wav", ".m4a"}
    ALL_FORMATS = SUPPORTED_FORMATS | {".mp3"}

    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def to_mp3(input_path: Path, output_path: Path) -> Path:
        """
        Convert video/audio file to MP3 optimized for Whisper.
        Always re-encodes to ensure correct format and small size.
        """
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "32k",
            "-y",
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed:\n{result.stderr[-500:]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg and add to PATH")


class WhisperTranscriber:
    """Transcribe audio using OpenAI Whisper API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required. Set it in .env file")
        # Explicitly use official OpenAI endpoint, ignore OPENAI_BASE_URL env var
        self.client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

    def transcribe(
        self,
        audio_path: Path,
        language: str = "vi",
        prompt: Optional[str] = None
    ) -> dict:
        """Transcribe audio file using Whisper API"""
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"       File size: {file_size_mb:.1f} MB")

        if file_size_mb > 24:
            raise ValueError(
                f"Audio file too large ({file_size_mb:.1f}MB). "
                f"Whisper API limit is 25MB. Please split the audio first."
            )

        # Use temp file with ASCII name for API compatibility
        temp_path = Path(os.environ.get("TEMP", "/tmp")) / f"whisper_{uuid.uuid4().hex[:8]}.mp3"

        try:
            shutil.copy2(audio_path, temp_path)

            with open(temp_path, "rb") as audio_file:
                # File parameter should be a file object, not a tuple
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language != "auto" else None,
                    response_format="verbose_json",
                    prompt=prompt
                )

        finally:
            if temp_path.exists():
                temp_path.unlink()

        segments = []
        if hasattr(response, "segments") and response.segments:
            segments = [
                {"start": seg.start, "end": seg.end, "text": seg.text}
                for seg in response.segments
            ]

        return {"text": response.text, "segments": segments}


class TranscriptWriter:
    """Write transcript to files"""

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"

    @staticmethod
    def write_txt(transcript: dict, output_path: Path, with_timestamps: bool = True):
        """Write transcript to TXT file"""
        with open(output_path, "w", encoding="utf-8") as f:
            if with_timestamps and transcript.get("segments"):
                for segment in transcript["segments"]:
                    timestamp = TranscriptWriter.format_timestamp(segment["start"])
                    f.write(f"{timestamp} {segment['text'].strip()}\n")
            else:
                f.write(transcript["text"])


def process_file(
    input_path: Path,
    output_dir: Optional[Path] = None,
    language: str = "vi",
    keep_mp3: bool = False,
    prompt: Optional[str] = None,
    with_timestamps: bool = True
) -> Tuple[bool, str]:
    """Process a single video/audio file"""

    if not input_path.exists():
        return False, f"File not found: {input_path}"

    if input_path.suffix.lower() not in VideoConverter.ALL_FORMATS:
        return False, f"Unsupported format: {input_path.suffix}"

    # Determine output paths
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_txt = output_dir / f"{input_path.stem}.txt"
    else:
        output_txt = input_path.with_suffix(".txt")

    if output_txt.exists():
        return True, f"Skipped (already exists): {output_txt}"

    if not VideoConverter.check_ffmpeg():
        return False, "FFmpeg not found. Please install FFmpeg and add to PATH"

    # Use temp dir for converted MP3 to avoid collisions
    temp_dir = Path(os.environ.get("TEMP", "/tmp"))
    mp3_path = temp_dir / f"convert_{uuid.uuid4().hex[:8]}.mp3"

    try:
        print(f"\n{'='*60}")
        print(f"Processing: {input_path.name}")
        print(f"{'='*60}")

        # Step 1: Convert to MP3 (always re-encode)
        print("[1/3] Converting to MP3...")
        VideoConverter.to_mp3(input_path, mp3_path)
        mp3_size_mb = mp3_path.stat().st_size / (1024 * 1024)
        print(f"       Converted: {mp3_size_mb:.1f} MB")

        # Optionally keep MP3 alongside original
        if keep_mp3 or Config.KEEP_MP3:
            keep_path = input_path.with_suffix(".mp3")
            shutil.copy2(mp3_path, keep_path)
            print(f"       Kept MP3: {keep_path.name}")

        # Step 2: Transcribe
        print("[2/3] Transcribing with Whisper API...")
        transcriber = WhisperTranscriber(Config.OPENAI_API_KEY)
        transcript = transcriber.transcribe(mp3_path, language, prompt)
        seg_count = len(transcript.get("segments", []))
        print(f"       Got {seg_count} segments")

        # Step 3: Write output
        print("[3/3] Writing transcript...")
        TranscriptWriter.write_txt(transcript, output_txt, with_timestamps)
        print(f"       Output: {output_txt}")

        return True, f"Success: {output_txt}"

    except Exception as e:
        return False, f"Error: {str(e)}"

    finally:
        # Always clean up temp MP3
        if mp3_path.exists():
            mp3_path.unlink()


def batch_process(
    input_dir: Path,
    output_dir: Optional[Path] = None,
    language: str = "vi",
    keep_mp3: bool = False,
    prompt: Optional[str] = None,
    with_timestamps: bool = True
) -> List[Tuple[bool, str]]:
    """Process all supported files in a directory"""
    results = []

    # Collect files, deduplicate by stem (prefer mp4/mkv over mp3)
    seen_stems = {}
    for ext in VideoConverter.ALL_FORMATS:
        for f in input_dir.glob(f"*{ext}"):
            stem = f.stem
            if stem not in seen_stems:
                seen_stems[stem] = f
            else:
                # Prefer non-MP3 source (original video)
                existing = seen_stems[stem]
                if existing.suffix.lower() == ".mp3" and ext != ".mp3":
                    seen_stems[stem] = f

    video_files = sorted(seen_stems.values())

    if not video_files:
        print(f"No supported video files found in: {input_dir}")
        return results

    print(f"\nFound {len(video_files)} file(s) to process")

    for video_file in video_files:
        result = process_file(video_file, output_dir, language, keep_mp3, prompt, with_timestamps)
        results.append(result)
        print(result[1])

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert OBS recordings to text transcripts using OpenAI Whisper API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i recording.mkv
  %(prog)s -i recording.mp4 -o ./transcripts/
  %(prog)s -i ./obs-recordings/ --language en
  %(prog)s -i recording.flv --keep-mp3
        """
    )

    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input file or directory path")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output directory (default: same as input)")
    parser.add_argument("-l", "--language", type=str, default=Config.DEFAULT_LANGUAGE,
                        help="Language code (default: %(default)s)")
    parser.add_argument("--keep-mp3", action="store_true",
                        help="Keep converted MP3 files alongside originals")
    parser.add_argument("--prompt", type=str, default=None,
                        help="Optional prompt to improve transcription quality")
    parser.add_argument("--no-timestamps", action="store_true",
                        help="Output plain text without timestamps")

    args = parser.parse_args()

    if not Config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in .env file")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else None
    with_timestamps = not args.no_timestamps

    if input_path.is_file():
        success, message = process_file(
            input_path, output_dir, args.language,
            args.keep_mp3, args.prompt, with_timestamps
        )
        print(message)
        sys.exit(0 if success else 1)
    else:
        results = batch_process(
            input_path, output_dir, args.language,
            args.keep_mp3, args.prompt, with_timestamps
        )

        success_count = sum(1 for r in results if r[0])
        fail_count = len(results) - success_count

        print(f"\n{'='*60}")
        print(f"Summary: {success_count} succeeded, {fail_count} failed")
        print(f"{'='*60}")

        sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
