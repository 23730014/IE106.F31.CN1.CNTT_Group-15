# ClearGov - Công cụ đơn giản hóa thủ tục hành chính

## Phiên bản 3: AI Vietnamese TTS

Prototype gồm:

- Vue.js 3 + Vite
- FastAPI
- NLP ánh xạ câu trả lời vào fields
- **Vietnamese Neural TTS** qua `edge-tts`
- Giọng mặc định: `vi-VN-HoaiMyNeural`
- Tốc độ đọc: `-20%`
- Tự động đọc câu hỏi mới
- Nút 🔊 đọc lại câu hỏi
- Nhập bằng giọng nói
- Form Preview

`edge-tts` là thư viện Python sử dụng dịch vụ text-to-speech trực tuyến của Microsoft Edge. Nó cho phép chọn neural voice và tạo file MP3 từ văn bản.

## 1. Chạy Backend

Mở Terminal 1:

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Chạy:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

## 2. Chạy Frontend

Mở Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Mở:

```text
http://localhost:5173
```

## 3. Cách hoạt động của AI TTS

```text
Vue.js
   |
   | "Bác sinh năm bao nhiêu ạ?"
   v
FastAPI /api/tts
   |
   v
edge-tts
   |
   v
Microsoft Edge Neural TTS
   |
   v
MP3
   |
   v
Vue.js Audio
   |
   v
🔊 Giọng tiếng Việt
```

## 4. Giọng đọc

Mặc định:

```text
vi-VN-HoaiMyNeural
```

Nếu muốn thử giọng nam, đổi trong `App.vue`:

```javascript
voice: 'vi-VN-NamMinhNeural'
```

Có thể kiểm tra các voice đang có bằng:

```bash
edge-tts --list-voices
```

## 5. Lưu ý

Phiên bản này cần Internet vì backend gọi dịch vụ TTS trực tuyến.

Nếu muốn chạy hoàn toàn offline, có thể nâng cấp sang VieNeu-TTS hoặc một mô hình TTS tiếng Việt chạy local.

## 6. Ví dụ

ClearGov sẽ hỏi:

> Bác sinh năm bao nhiêu ạ?

Frontend gửi:

```json
{
  "text": "Bác sinh năm bao nhiêu ạ?",
  "voice": "vi-VN-HoaiMyNeural",
  "rate": "-20%",
  "volume": "+0%"
}
```

Backend trả về audio MP3 và Vue.js phát trực tiếp.
