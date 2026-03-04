# OBS Video → Transcript Tool

Công cụ CLI Python để chuyển đổi bản ghi hình OBS thành bản văn bản bằng OpenAI Whisper API.

## Tính năng

- Chuyển đổi video/audio (MKV, MP4, MOV, FLV, AVI, WEBM, MP3, WAV, M4A) sang văn bản
- Xử lý hàng loạt cả thư mục
- Xuất transcript có timestamps `[HH:MM:SS] text`
- Hỗ trợ Tiếng Việt và đa ngôn ngữ
- Tự động chuyển đổi sang MP3 bằng FFmpeg
- Tự động xóa file tạm

## Yêu cầu

- Python 3.10+
- FFmpeg (phải có trong PATH)
- OpenAI API key

### Kiểm tra cài đặt

Trước khi bắt đầu, kiểm tra xem máy đã cài Python và FFmpeg chưa:

```bash
# Kiểm tra phiên bản Python (yêu cầu 3.10+)
python --version
# Hoặc trên một số hệ thống:
python3 --version

# Kiểm tra FFmpeg
ffmpeg -version
```

Nếu thiếu, cài đặt:
- **Python**: Tải từ [python.org](https://www.python.org/downloads/)
- **FFmpeg**: Tải từ [ffmpeg.org](https://ffmpeg.org/download.html)

## Cài đặt

1. Clone repository:
```bash
git clone <repo-url>
cd video-to-text-whisper
```

2. (Khuyến nghị) Tạo virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Cài đặt FFmpeg:
- **Windows**: Tải từ [ffmpeg.org](https://ffmpeg.org/download.html) và thêm vào PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` hoặc `sudo yum install ffmpeg`

5. Cấu hình môi trường:
```bash
cp .env.example .env
# Edit .env và thêm OPENAI_API_KEY của bạn
```

Lấy API key tại: https://platform.openai.com/api-keys

## Cách sử dụng

### Xử lý một file
```bash
python main.py -i recording.mkv
```

### Chỉ định thư mục output
```bash
python main.py -i recording.mp4 -o ./transcripts/
```

### Xử lý hàng loạt thư mục
```bash
python main.py -i ./obs-recordings/
```

### Chỉ định ngôn ngữ
```bash
python main.py -i recording.mp4 --language en
```

### Giữ lại file MP3 tạm
```bash
python main.py -i recording.flv --keep-mp3
```

### Dùng prompt để tăng độ chính xác
```bash
python main.py -i recording.mp4 --prompt "Thảo luận kỹ thuật về AI và machine learning"
```

## Định dạng output

**output.txt**:
```
[00:00:00] Xin chào mọi người, hôm nay mình sẽ hướng dẫn
[00:00:03] cách cài đặt và sử dụng...
[00:00:07] Đầu tiên chúng ta cần mở terminal lên
```

## Cấu hình

Edit file `.env`:

```env
OPENAI_API_KEY=sk-your-api-key-here
DEFAULT_LANGUAGE=vi
OUTPUT_DIR=
KEEP_MP3=false
```

## Tham số CLI

| Tham số | Ngắn | Mô tả | Mặc định |
|---------|------|-------|----------|
| `--input` | `-i` | File hoặc thư mục input | (bắt buộc) |
| `--output` | `-o` | Thư mục output | Cùng với input |
| `--language` | `-l` | Mã ngôn ngữ | `vi` |
| `--keep-mp3` | | Giữ lại file MP3 tạm | `false` |
| `--prompt` | | Prompt tùy chỉnh | `null` |

## Các ngôn ngữ hỗ trợ

Afrikaans, Ả Rập, Armenia, Azerbaijan, Belarus, Bosnia, Bulgaria, Catalan, Trung Quốc, Croatia, Séc, Đan Mạch, Hà Lan, Tiếng Anh, Estonia, Phần Lan, Pháp, Galicia, Đức, Hy Lạp, Hebrew, Hindi, Hungary, Iceland, Indonesia, Ý, Nhật Bản, Kannada, Kazakh, Hàn Quốc, Latvia, Lithuania, Macedonia, Mã Lai, Marathi, Maori, Nepal, Na Uy, Ba Tư, Ba Lan, Bồ Đào Nha, Romania, Nga, Serbia, Slovakia, Slovenia, Tây Ban Nha, Swahili, Thụy Điển, Tagalog, Tamil, Thái, Thổ Nhĩ Kỳ, Ukraine, Urdu, Tiếng Việt, và Welsh.

## Giới hạn

- Whisper API giới hạn 25MB mỗi request
- FFmpeg tối ưu giúp giảm kích thước file đáng kể
- Xử lý tuần tự (không parallel) để tránh rate limit

## Cấu trúc dự án

```
video-to-text-whisper/
├── main.py              # Entry point CLI
├── requirements.txt     # Python dependencies
├── .env                 # API keys (không commit git)
├── .env.example         # Mẫu cấu hình
├── .gitignore
├── README.md            # Hướng dẫn tiếng Anh
└── README_VI.md         # Hướng dẫn tiếng Việt
```

## Giấy phép

MIT
