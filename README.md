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


## 7. Lấy thông tin từ hình ảnh (OCR)

Phiên bản này hỗ trợ tải ảnh giấy tờ/CCCD và tự động đọc thông tin bằng **Tesseract.js** ngay trên trình duyệt.

Luồng hoạt động:

```text
Tải ảnh CCCD/giấy tờ
        ↓
Tesseract.js OCR (tiếng Việt + tiếng Anh)
        ↓
Văn bản OCR
        ↓
FastAPI /api/extract
        ↓
NLP trích xuất: họ tên, năm sinh, CCCD, địa chỉ
        ↓
Tự điền Form Preview
```

### Cài đặt

Sau khi cập nhật project:

```bash
cd frontend
npm install
npm run dev
```

Không cần thêm API key cho OCR. Lần đầu OCR có thể cần Internet để tải dữ liệu ngôn ngữ Tesseract.

### Lưu ý

- Nên dùng ảnh rõ, đủ sáng, chụp thẳng giấy tờ.
- OCR có thể đọc sai ký tự; người dùng vẫn cần kiểm tra lại trước khi xác nhận hồ sơ.
- Ảnh được xử lý OCR ở phía trình duyệt trong prototype này.


### OCR trích xuất 4 trường từ ảnh

Bản Image OCR mới sử dụng parser theo **nhãn trường** thay vì chỉ tìm dữ liệu tự do. Vì vậy các dạng như sau được hỗ trợ:

- `SCCCD: 237300140015` → `id_number = 237300140015`
- `Họ Tên: Phạm Nguyễn Đăng Duy` → `name = Phạm Nguyễn Đăng Duy`
- `Năm sinh: 2000` → `birth_year = 2000`
- `Địa chỉ: 12/11 HTP, TP.HCM` → `address = 12/11 HTP, TP.HCM`

Ngoài ra có xử lý OCR không dấu như `Ho Ten`, `Nam sinh`, `Dia chi` và tiền xử lý ảnh (phóng to + grayscale + tăng tương phản) trước khi Tesseract nhận diện.

## 8. Chỉnh sửa thông tin trước khi xác nhận

Khi OCR đọc đủ thông tin từ hình ảnh, màn hình hoàn thành hồ sơ hiển thị các trường dưới dạng ô nhập liệu có thể chỉnh sửa.

Người dùng có thể sửa:
- Họ và tên
- Năm sinh
- Số căn cước công dân
- Địa chỉ

Nút **Xác nhận hồ sơ** sẽ kiểm tra dữ liệu trước khi xác nhận:
- Họ tên không được để trống.
- Năm sinh phải có 4 chữ số và nằm trong khoảng hợp lệ.
- CCCD phải đúng 12 chữ số.
- Địa chỉ không được để trống.


## 8. Chú thích code

Code phiên bản này đã được thêm chú thích theo từng khu vực để dễ đọc và bảo trì.

### `frontend/src/App.vue`

- **1. IMPORT THƯ VIỆN**: Vue và Tesseract.js.
- **2. CẤU HÌNH API BACKEND**: URL dùng để gọi FastAPI.
- **3. CẤU HÌNH CÁC TRƯỜNG HỒ SƠ**: Họ tên, năm sinh, CCCD, địa chỉ.
- **4. STATE / DỮ LIỆU FORM**: dữ liệu có thể chỉnh sửa trước khi xác nhận.
- **5. STATE ĐIỀU KHIỂN GIAO DIỆN**: xác định trang hiện tại.
- **6. UPLOAD ẢNH + OCR**: đọc chữ từ ảnh và trích xuất thông tin.
- **7. ĐƯA KẾT QUẢ OCR VÀO FORM**: tự điền dữ liệu để người dùng kiểm tra.
- **8. BẮT ĐẦU / RESET HỒ SƠ**: khởi tạo hồ sơ mới.
- **9. XÁC NHẬN HỒ SƠ**: kiểm tra dữ liệu và chuyển sang trạng thái đã nộp.
- **10. LÀM LẠI**: xóa hồ sơ cũ và quay về trang đầu.
- **11–12. HÀM TIỆN ÍCH**: scroll và text-to-speech.
- **13A. TRANG ĐẦU**: upload ảnh hoặc bắt đầu hồ sơ.
- **13B. TRANG CHỈNH SỬA**: người dùng được phép sửa trước khi xác nhận.
- **13C. TRANG ĐÃ NỘP**: chỉ hiển thị thông tin, không cho sửa.

### Luồng xử lý

```text
Trang đầu
  ↓
Upload ảnh
  ↓
OCR
  ↓
Trích xuất Họ tên / Năm sinh / CCCD / Địa chỉ
  ↓
Chỉnh sửa trước khi xác nhận
  ↓
Xác nhận hồ sơ
  ↓
OK
  ↓
Trang hồ sơ đã nộp (READ-ONLY)
  ↓
Làm lại
  ↓
Trang đầu
```

### Nếu muốn chỉnh sửa code

- Muốn sửa **OCR** → tìm `6. UPLOAD ẢNH + OCR`.
- Muốn sửa **các trường dữ liệu** → tìm `3. CẤU HÌNH CÁC TRƯỜNG HỒ SƠ`.
- Muốn sửa **validation/xác nhận** → tìm `9. XÁC NHẬN HỒ SƠ`.
- Muốn sửa **nút Làm lại** → tìm `10. LÀM LẠI`.
- Muốn sửa **trang read-only sau khi nộp** → tìm `13C. TRANG HỒ SƠ ĐÃ NỘP - READ ONLY`.


## 9. Fix lỗi build `await can only be used inside an async function`

Hàm `speak()` sử dụng `await fetch(...)` và `await response.blob()`, vì vậy bắt buộc phải khai báo:

```js
async function speak(text) {
```

Phiên bản này đã sửa lỗi chú thích trước đó làm biến dạng dòng khai báo hàm thành `async // ...`, khiến Vite/ESBuild báo lỗi tại dòng `await`.
