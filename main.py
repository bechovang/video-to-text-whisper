#!/usr/bin/env python3
"""
OBS Video → Transcript Tool
Convert video files to text transcripts using OpenAI Whisper API
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package. Run: pip install -r requirements.txt")
    print(f"Details: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()


class Config:
    """Configuration management"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "vi")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "")
    KEEP_MP3 = os.getenv("KEEP_MP3", "false").lower() == "true"


class VideoConverter:
    """Convert video files to MP3 using FFmpeg"""

    SUPPORTED_FORMATS = {".mkv", ".mp4", ".mov", ".flv", ".avi", ".webm", ".mp3", ".wav", ".m4a"}

    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def to_mp3(input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert video/audio file to MP3 optimized for Whisper

        Args:
            input_path: Path to input file
            output_path: Path to output MP3 (auto-generated if None)

        Returns:
            Path to output MP3 file
        """
        if output_path is None:
            output_path = input_path.with_suffix(".mp3")

        # FFmpeg command optimized for Whisper
        # -vn: no video, -ar 16000: 16kHz sample rate, -ac 1: mono, -ab 128k: bitrate
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",
            "-ar", "16000",
            "-ac", "1",
            "-ab", "128k",
            "-y",  # Overwrite output file
            str(output_path)
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg conversion failed: {e.stderr}")


class WhisperTranscriber:
    """Transcribe audio using OpenAI Whisper API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required. Set it in .env file")
        self.client = OpenAI(api_key=api_key)

    def transcribe(
        self,
        audio_path: Path,
        language: str = "vi",
        prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file using Whisper API

        Args:
            audio_path: Path to MP3 file
            language: Language code (vi, en, auto, etc.)
            prompt: Optional prompt to improve transcription

        Returns:
            Dictionary with 'text' and 'segments' (with timestamps)
        """
        # Check file size (Whisper API limit: 25MB)
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            raise ValueError(
                f"Audio file too large ({file_size_mb:.1f}MB). "
                f"Whisper API limit is 25MB. Please split the audio first."
            )

        with open(audio_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language != "auto" else None,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                prompt=prompt
            )

        return {
            "text": response.text,
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                }
                for seg in response.segments
            ] if hasattr(response, 'segments') else []
        }


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
        """
        Write transcript to TXT file

        Format:
        [HH:MM:SS] Text here...
        """
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
    prompt: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Process a single video file

    Returns:
        Tuple of (success, message)
    """
    # Validate input
    if not input_path.exists():
        return False, f"File not found: {input_path}"

    if input_path.suffix.lower() not in VideoConverter.SUPPORTED_FORMATS:
        return False, f"Unsupported format: {input_path.suffix}"

    # Determine output paths
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_txt = output_dir / f"{input_path.stem}.txt"
    else:
        output_txt = input_path.with_suffix(".txt")

    # Check if already transcribed
    if output_txt.exists():
        return True, f"Skipped (already exists): {output_txt}"

    # Check FFmpeg
    if not VideoConverter.check_ffmpeg():
        return False, "FFmpeg not found. Please install FFmpeg and add to PATH"

    try:
        print(f"\n{'='*60}")
        print(f"Processing: {input_path.name}")
        print(f"{'='*60}")

        # Step 1: Convert to MP3
        print("[1/3] Converting to MP3...")
        mp3_path = input_path.with_suffix(".mp3")
        VideoConverter.to_mp3(input_path, mp3_path)
        mp3_size_mb = mp3_path.stat().st_size / (1024 * 1024)
        print(f"       Created: {mp3_path.name} ({mp3_size_mb:.1f} MB)")

        # Step 2: Transcribe
        print("[2/3] Transcribing with Whisper API...")
        transcriber = WhisperTranscriber(Config.OPENAI_API_KEY)
        transcript = transcriber.transcribe(mp3_path, language, prompt)
        print(f"       Transcribed {len(transcript.get('segments', []))} segments")

        # Step 3: Write output
        print("[3/3] Writing transcript...")
        TranscriptWriter.write_txt(transcript, output_txt)
        print(f"       Output: {output_txt}")

        # Cleanup
        if not keep_mp3 and not Config.KEEP_MP3:
            mp3_path.unlink()
            print(f"       Cleaned up: {mp3_path.name}")

        return True, f"Success: {output_txt}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def batch_process(
    input_dir: Path,
    output_dir: Optional[Path] = None,
    language: str = "vi",
    keep_mp3: bool = False,
    prompt: Optional[str] = None
) -> List[Tuple[bool, str]]:
    """Process all supported files in a directory"""
    results = []

    video_files = []
    for ext in VideoConverter.SUPPORTED_FORMATS:
        video_files.extend(input_dir.glob(f"*{ext}"))

    if not video_files:
        print(f"No supported video files found in: {input_dir}")
        return results

    print(f"\nFound {len(video_files)} file(s) to process")

    for video_file in sorted(video_files):
        result = process_file(video_file, output_dir, language, keep_mp3, prompt)
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

    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input file or directory path"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output directory (default: same as input)"
    )

    parser.add_argument(
        "-l", "--language",
        type=str,
        default=Config.DEFAULT_LANGUAGE,
        help="Language code (default: %(default)s)"
    )

    parser.add_argument(
        "--keep-mp3",
        action="store_true",
        help="Keep temporary MP3 files"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Optional prompt to improve transcription quality"
    )

    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Output plain text without timestamps"
    )

    args = parser.parse_args()

    # Validate API key
    if not Config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with your OpenAI API key")
        sys.exit(1)

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else None

    # Process single file or directory
    if input_path.is_file():
        success, message = process_file(
            input_path,
            output_dir,
            args.language,
            args.keep_mp3,
            args.prompt
        )
        print(message)
        sys.exit(0 if success else 1)
    else:
        results = batch_process(
            input_path,
            output_dir,
            args.language,
            args.keep_mp3,
            args.prompt
        )

        # Summary
        success_count = sum(1 for r in results if r[0])
        fail_count = len(results) - success_count

        print(f"\n{'='*60}")
        print(f"Summary: {success_count} succeeded, {fail_count} failed")
        print(f"{'='*60}")

        sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
