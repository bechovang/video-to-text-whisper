# OBS Video → Transcript Tool

Công cụ CLI Python để chuyển đổi bản ghi hình OBS thành bản văn bản bằng OpenAI Whisper API.

## Tính năng

- Chuyển đổi video/audio (MKV, MP4, MOV, FLV, AVI, WEBM, MP3, WAV, M4A) sang văn bản
- Xử lý hàng loạt cả thư mục (tự động dedup file trùng tên)
- **Tự động tách audio** cho video dài (không giới hạn 25MB)
- 3 chế độ output: có timestamp, chỉ text, hoặc cả hai
- Hỗ trợ Tiếng Việt và đa ngôn ngữ (50+ ngôn ngữ)
- Tự động chuyển đổi sang MP3 bằng FFmpeg (64k mono, tối ưu cho API)
- Tự động xóa file tạm trong thư mục hệ thống (%TEMP%)
- Hỗ trợ filename có emoji/tiếng Việt
- File .env có quyền cao hơn system environment variables

## Yêu cầu

- Python 3.10+
- FFmpeg (phải có trong PATH)
- OpenAI API key (official OpenAI, không phải OpenRouter)

### Kiểm tra cài đặt

Trước khi bắt đầu, kiểm tra xem máy đã cài Python và FFmpeg chưa:

```bash
# Kiểm tra phiên bản Python (yêu cầu 3.10+)
python --version

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

### Xử lý một file (chỉ text - mặc định)
```bash
python main.py -i recording.mkv
```

### Có timestamp
```bash
python main.py -i recording.mp4 --timestamps
```

### Tạo cả 2 file (có timestamp và chỉ text)
```bash
python main.py -i recording.mp4 --both
# Tạo: file_ts.txt (có timestamp) và file_plain.txt (chỉ text)
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

### Thông dụng
```bash
python main.py -i ./video/ -o ./transcripts/
```

## Định dạng output

**output.txt** (mặc định - chỉ text):
```
Xin chào mọi người, hôm nay mình sẽ hướng dẫn cách cài đặt và sử dụng... Đầu tiên chúng ta cần mở terminal lên
```

**output.txt** (--timestamps):
```
[00:00:00] Xin chào mọi người, hôm nay mình sẽ hướng dẫn
[00:00:03] cách cài đặt và sử dụng...
[00:00:07] Đầu tiên chúng ta cần mở terminal lên
```

## Cấu hình

Edit file `.env`:

```env
OPENAI_API_KEY=sk-proj-your-key-here
DEFAULT_LANGUAGE=vi
OUTPUT_DIR=
KEEP_MP3=false
```

**Lưu ý:** File `.env` sẽ override system environment variables.

## Tham số CLI

| Tham số | Ngắn | Mô tả | Mặc định |
|---------|------|-------|----------|
| `--input` | `-i` | File hoặc thư mục input | (bắt buộc) |
| `--output` | `-o` | Thư mục output | Cùng với input |
| `--language` | `-l` | Mã ngôn ngữ | `vi` |
| `--keep-mp3` | | Giữ lại file MP3 tạm | `false` |
| `--prompt` | | Prompt tùy chỉnh | `null` |
| `--timestamps` | | Output có timestamps | `false` |
| `--both` | | Tạo cả 2 file (có và không timestamp) | `false` |

## Các ngôn ngữ hỗ trợ

Afrikaans, Ả Rập, Armenia, Azerbaijan, Belarus, Bosnia, Bulgaria, Catalan, Trung Quốc, Croatia, Séc, Đan Mạch, Hà Lan, Tiếng Anh, Estonia, Phần Lan, Pháp, Galicia, Đức, Hy Lạp, Hebrew, Hindi, Hungary, Iceland, Indonesia, Ý, Nhật Bản, Kannada, Kazakh, Hàn Quốc, Latvia, Lithuania, Macedonia, Mã Lai, Marathi, Maori, Nepal, Na Uy, Ba Tư, Ba Lan, Bồ Đào Nha, Romania, Nga, Serbia, Slovakia, Slovenia, Tây Ban Nha, Swahili, Thụy Điển, Tagalog, Tamil, Thái, Thổ Nhĩ Kỳ, Ukraine, Urdu, Tiếng Việt, và Welsh.

## Xử lý video dài

- **Tự động tách audio** thành các phần 10 phút khi file > 24MB
- Video bao lâu cũng được - tự động xử lý từng phần và gộp kết quả
- Timestamps được điều chỉnh tự động khớp với thời gian thực

## Changelog

### v1.1.0
- ✨ Tự động tách audio cho video dài (không giới hạn 25MB)
- ✨ Tùy chọn `--no-timestamps` để chỉ lấy text
- ✨ Tùy chọn `--both` để tạo cả 2 file
- 🎨 Tăng bitrate 32k → 64k (chất lượng tốt hơn)
- ⚡ Dùng `text` format khi không cần timestamp (nhanh hơn)

### v1.0.0
- Initial release
- FFmpeg conversion to 32k mono MP3
- OpenAI Whisper API integration
- Batch processing with deduplication
- Windows UTF-8 console support (emoji filenames)
- .env override system environment variables

## Cấu trúc dự án

```
video-to-text-whisper/
├── main.py              # Entry point CLI
├── requirements.txt     # Python dependencies
├── .env                 # API keys (không commit git)
├── .env.example         # Mẫu cấu hình
├── .gitignore
├── README.md            # Hướng dẫn tiếng Việt
└── README_EN.md         # Hướng dẫn tiếng Anh
```

## Giấy phép

MIT
