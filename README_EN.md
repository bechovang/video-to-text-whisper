# OBS Video → Transcript Tool

Python CLI tool to convert OBS recordings to text transcripts using OpenAI Whisper API.

## Features

- Convert video/audio files (MKV, MP4, MOV, FLV, AVI, WEBM, MP3, WAV, M4A) to text
- Batch process entire directories (auto-deduplicate files)
- **Auto-split audio** for long videos (no 25MB limit)
- 3 output modes: with timestamps, plain text only, or both
- Vietnamese and multi-language support (50+ languages)
- Automatic MP3 conversion using FFmpeg (64k mono, optimized for API)
- Clean temporary files from system temp directory (%TEMP%)
- Support emoji/Vietnamese filenames
- .env file overrides system environment variables

## Requirements

- Python 3.10+
- FFmpeg (must be in system PATH)
- OpenAI API key (official OpenAI, not OpenRouter)

### Check installation

Before starting, verify your system has Python and FFmpeg installed:

```bash
# Check Python version (requires 3.10+)
python --version
# Or on some systems:
python3 --version

# Check FFmpeg
ffmpeg -version
```

If missing, install:
- **Python**: Download from [python.org](https://www.python.org/downloads/)
- **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd video-to-text-whisper
```

2. (Recommended) Create virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

5. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### Single file (plain text - default)
```bash
python main.py -i recording.mkv
```

### With timestamps
```bash
python main.py -i recording.mp4 --timestamps
```

### Create both files (with and without timestamps)
```bash
python main.py -i recording.mp4 --both
# Creates: file_ts.txt (with timestamps) and file_plain.txt (plain text)
```

### Custom output directory
```bash
python main.py -i recording.mp4 -o ./transcripts/
```

### Batch process directory
```bash
python main.py -i ./obs-recordings/
```

### Specify language
```bash
python main.py -i recording.mp4 --language en
```

### Keep temporary MP3 files
```bash
python main.py -i recording.flv --keep-mp3
```

### Use prompt for better accuracy
```bash
python main.py -i recording.mp4 --prompt "Technical discussion about AI and machine learning"
```

### Common usage
```bash
python main.py -i ./video/ -o ./transcripts/
```

## Output format

**output.txt** (default - plain text):
```
Xin chào mọi người, hôm nay mình sẽ hướng dẫn cách cài đặt và sử dụng... Đầu tiên chúng ta cần mở terminal lên
```

**output.txt** (--timestamps):
```
[00:00:00] Xin chào mọi người, hôm nay mình sẽ hướng dẫn
[00:00:03] cách cài đặt và sử dụng...
[00:00:07] Đầu tiên chúng ta cần mở terminal lên
```

## Configuration

Edit `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
DEFAULT_LANGUAGE=vi
OUTPUT_DIR=
KEEP_MP3=false
```

**Note:** `.env` file will override system environment variables.

## CLI Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--input` | `-i` | Input file or directory | (required) |
| `--output` | `-o` | Output directory | Same as input |
| `--language` | `-l` | Language code | `vi` |
| `--keep-mp3` | | Keep temporary MP3 files | `false` |
| `--prompt` | | Custom prompt for transcription | `null` |
| `--timestamps` | | Output with timestamps | `false` |
| `--both` | | Create both files (with and without timestamps) | `false` |

## Supported languages

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

## Long video handling

- **Auto-split audio** into 10-minute chunks when file > 24MB
- No video length limit - automatically processes each part and merges results
- Timestamps are automatically adjusted to match real time

## Changelog

### v1.1.0
- ✨ Auto-split audio for long videos (no 25MB limit)
- ✨ `--no-timestamps` option for plain text output
- ✨ `--both` option to create both file types
- 🎨 Increased bitrate 32k → 64k (better quality)
- ⚡ Use `text` format when timestamps not needed (faster)

### v1.0.0
- Initial release
- FFmpeg conversion to 32k mono MP3
- OpenAI Whisper API integration
- Batch processing with deduplication
- Windows UTF-8 console support (emoji filenames)
- .env override system environment variables

## Project structure

```
video-to-text-whisper/
├── main.py              # Entry point CLI
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not in git)
├── .env.example         # Environment template
├── .gitignore
├── README.md            # Vietnamese guide
└── README_EN.md         # English guide
```

## License

MIT
