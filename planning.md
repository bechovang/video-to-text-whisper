# 🎙️ OBS Video → Transcript Tool
> Python CLI · FFmpeg · OpenAI Whisper API

---

## 📌 Mục tiêu

Tự động hóa pipeline:
**File OBS (MKV/MP4)** → **FFmpeg convert → MP3** → **Whisper API** → **Output TXT + SRT**

---

## 🗂️ Cấu trúc thư mục

```
obs-transcriber/
├── main.py              # Entry point CLI
├── config.py            # API key, cấu hình mặc định
├── transcriber/
│   ├── __init__.py
│   ├── converter.py     # FFmpeg: video → mp3
│   ├── whisper_api.py   # Gọi OpenAI Whisper API
│   └── writer.py        # Ghi file TXT, SRT
├── requirements.txt
├── .env                 # OPENAI_API_KEY (không commit)
├── .env.example
└── README.md
```

---

## ⚙️ Tech Stack

| Thành phần | Công cụ |
|---|---|
| Ngôn ngữ | Python 3.10+ |
| Audio convert | `ffmpeg` (subprocess) |
| Transcription | OpenAI Whisper API (`whisper-1`) |
| CLI | `argparse` |
| Env config | `python-dotenv` |
| HTTP Client | `openai` SDK |

---

## 🔄 Pipeline chi tiết

```
┌─────────────────┐
│  Input: video   │  .mkv / .mp4 / .mov / .flv (OBS output)
│  (file hoặc     │
│   thư mục)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   converter.py  │  ffmpeg -i input.mkv
│   FFmpeg        │  -vn -ar 16000 -ac 1 -ab 128k
│   → MP3         │  output.mp3
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  whisper_api.py │  POST /v1/audio/transcriptions
│  Whisper API    │  model=whisper-1
│                 │  language=vi (hoặc auto)
│                 │  response_format=verbose_json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   writer.py     │  → output.txt  (plain text)
│   Output        │  → output.srt  (có timestamp)
└─────────────────┘
```

---

## 📋 Các Phase triển khai

### Phase 1 — Setup & Config
- [ ] Tạo cấu trúc thư mục
- [ ] Cài dependencies: `pip install openai python-dotenv`
- [ ] Setup `.env` với `OPENAI_API_KEY`
- [ ] Viết `config.py` (đọc env, giá trị mặc định)

### Phase 2 — FFmpeg Converter (`converter.py`)
- [ ] Nhận `input_path` → validate file tồn tại
- [ ] Kiểm tra `ffmpeg` có trong PATH
- [ ] Chạy ffmpeg: convert sang MP3 16kHz mono (tối ưu cho Whisper)
- [ ] Lưu MP3 vào thư mục `tmp/` tạm thời
- [ ] Xóa MP3 tạm sau khi transcript xong
- [ ] Xử lý lỗi: file không hợp lệ, ffmpeg crash

### Phase 3 — Whisper API (`whisper_api.py`)
- [ ] Mở file MP3, gọi `client.audio.transcriptions.create()`
- [ ] Config: `model=whisper-1`, `language="vi"`, `response_format="verbose_json"`
- [ ] Parse response: lấy `text` và `segments` (có timestamp)
- [ ] Xử lý lỗi: API timeout, file quá lớn (giới hạn 25MB)
- [ ] Nếu MP3 > 25MB → tự động split bằng ffmpeg rồi ghép kết quả

### Phase 4 — Writer (`writer.py`)
- [ ] Ghi `output.txt`: plain text có timestamp mỗi segment `[HH:MM:SS] text`
- [ ] Tên output = tên file input (thay extension)
- [ ] Hỗ trợ custom output directory

### Phase 5 — CLI (`main.py`)
- [ ] `--input` / `-i`: path file hoặc thư mục (batch)
- [ ] `--output` / `-o`: thư mục output (default: cùng chỗ với input)
- [ ] `--language` / `-l`: ngôn ngữ (default: `vi`)
- [ ] `--keep-mp3`: không xóa file MP3 tạm
- [ ] Progress indicator khi đang xử lý

### Phase 6 — Batch Processing
- [ ] Nếu input là thư mục: quét tất cả `.mkv`, `.mp4`, `.mov`, `.flv`
- [ ] Xử lý tuần tự (không parallel — tránh rate limit API)
- [ ] Log: file nào thành công, file nào lỗi
- [ ] Skip file đã có transcript (kiểm tra output tồn tại)

---

## 💻 Cách dùng (CLI Examples)

```bash
# Một file
python main.py -i recording.mkv

# Chỉ định output folder
python main.py -i recording.mov -o ./transcripts/

# Batch cả thư mục (tự quét mkv/mp4/mov/flv)
python main.py -i ./obs-recordings/

# Tiếng Anh
python main.py -i recording.mp4 --language en

# Chỉ lấy TXT, không cần JSON
python main.py -i recording.flv --no-json
```

---

## 📦 `requirements.txt`

```
openai>=1.0.0
python-dotenv>=1.0.0
```

---

## ⚠️ Giới hạn cần lưu ý

| Vấn đề | Giải pháp |
|---|---|
| Whisper API tối đa **25MB** mỗi file | Tự động split MP3 nếu vượt |
| File video OBS có thể rất lớn (GB) | FFmpeg chỉ extract audio, MP3 nhỏ hơn nhiều |
| Rate limit API | Xử lý tuần tự + retry khi gặp lỗi 429 |
| Transcript tiếng Việt có thể sai | Set `language=vi` để Whisper ưu tiên |

---

## 🔑 FFmpeg command tối ưu cho Whisper

```bash
ffmpeg -i input.mkv \
  -vn \          # Bỏ video stream
  -ar 16000 \    # Sample rate 16kHz (Whisper yêu cầu)
  -ac 1 \        # Mono channel
  -ab 128k \     # Bitrate vừa đủ
  output.mp3
```

---

## 📁 Output mẫu

**output.txt**
```
[00:00:00] Xin chào mọi người, hôm nay mình sẽ hướng dẫn
[00:00:03] cách cài đặt và sử dụng...
[00:00:07] Đầu tiên chúng ta cần mở terminal lên
```

---

## ✅ Definition of Done

- [ ] Chạy được single file từ CLI (mkv/mp4/mov/flv)
- [ ] Chạy được batch cả thư mục
- [ ] Xuất `.txt` đúng format `[HH:MM:SS] text` mỗi segment
- [ ] Xử lý lỗi không crash toàn bộ
- [ ] README có hướng dẫn setup
