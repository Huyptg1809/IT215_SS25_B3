## 1. Cài đặt và Chạy
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Truy cập Swagger UI: http://127.0.0.1:8000/docs

## 2. Test Cases (7 Bẫy Dữ Liệu)
- **Bẫy 1:** Bài tập không tồn tại (`assignment_id = 999`) -> `404`
- **Bẫy 2:** Bài tập đã đóng (`assignment_id = 2`) -> `409`
- **Bẫy 3:** Nộp lần 4 (Quá 3 lần) -> `409`
- **Bẫy 4:** Đường dẫn độc hại (`../../main.py`) -> Sinh tên file UUID mới, bỏ qua tên gốc.
- **Bẫy 5:** Sai định dạng (`project.rar`) -> `400`
- **Bẫy 6:** Kích thước lớn (>20MB) -> `400` (Dùng `file.tell()` từ Spool RAM).
- **Bẫy 7:** Lỗi ghi file dở dang -> Block `try...except` tự động xóa file lỗi và báo `500`.

## 3. Cấu trúc
- `docs/analysis_design.md`: Báo cáo phân tích.
- `app/main.py`: Khởi chạy API.
- `app/services.py`: Logic nghiệp vụ (Tách biệt khỏi endpoint).
