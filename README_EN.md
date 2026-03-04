# OBS Video → Transcript Tool

Python CLI tool to convert OBS recordings to text transcripts using OpenAI Whisper API.

## Features

- Convert video/audio files (MKV, MP4, MOV, FLV, AVI, WEBM, MP3, WAV, M4A) to text
- Batch process entire directories
- Output transcripts with timestamps `[HH:MM:SS] text`
- Vietnamese and multi-language support
- Automatic MP3 conversion using FFmpeg
- Clean temporary files

## Requirements

- Python 3.10+
- FFmpeg (must be in system PATH)
- OpenAI API key

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

3. Install FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### Single file
```bash
python main.py -i recording.mkv
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

## Output format

**output.txt**:
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

## CLI Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--input` | `-i` | Input file or directory | (required) |
| `--output` | `-o` | Output directory | Same as input |
| `--language` | `-l` | Language code | `vi` |
| `--keep-mp3` | | Keep temporary MP3 files | `false` |
| `--prompt` | | Custom prompt for transcription | `null` |

## Supported languages

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

## Limitations

- Whisper API has a 25MB file size limit per request
- FFmpeg optimization reduces file size significantly
- Sequential processing (no parallel) to avoid rate limits

## Project structure

```
video-to-text-whisper/
├── main.py              # Entry point CLI
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not in git)
├── .env.example         # Environment template
├── .gitignore
└── README.md
```

## License

MIT
