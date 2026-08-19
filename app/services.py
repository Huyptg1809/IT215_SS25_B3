import os
import re
import uuid
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
STORAGE_BASE = "storage/submissions"
assignments = {
    1: {
        "id": 1,
        "title": "FastAPI CRUD",
        "deadline": "2026-08-15T23:59:59",
        "allowed_extensions": [".zip", ".pdf"],
        "max_size_mb": 20,
        "is_open": True,
    },
    2: {
        "id": 2,
        "title": "Python Final Project",
        "deadline": "2026-07-20T23:59:59",
        "allowed_extensions": [".zip"],
        "max_size_mb": 50,
        "is_open": False,
    },
}
submissions_db = []
def validate_student_data(student_id: str, student_name: str):
    student_id = student_id.strip()
    student_name = student_name.strip()
    if not student_id or not student_name:
        raise HTTPException(status_code=400, detail="Mã sinh viên và họ tên không được để trống.")
    if not re.match(r"^SV\d{6}$", student_id):
        raise HTTPException(status_code=400, detail="Mã sinh viên phải có định dạng SV + 6 chữ số (VD: SV000123).")
    return student_id, student_name
def validate_assignment(assignment_id: int):
    if assignment_id not in assignments:
        raise HTTPException(status_code=404, detail="Bài tập không tồn tại.")
    assignment = assignments[assignment_id]
    if not assignment["is_open"]:
        raise HTTPException(status_code=409, detail="Bài tập đã đóng.")
    deadline = datetime.fromisoformat(assignment["deadline"])
    if datetime.now() > deadline:
        raise HTTPException(status_code=409, detail="Đã quá hạn nộp bài.")
    return assignment
def check_attempt(student_id: str, assignment_id: int):
    attempts = len([s for s in submissions_db if s["student_id"] == student_id and s["assignment_id"] == assignment_id])
    next_attempt = attempts + 1
    if next_attempt > 3:
        raise HTTPException(status_code=409, detail="Bạn đã hết số lần nộp bài (tối đa 3 lần).")
    return next_attempt
def validate_file(file: UploadFile, allowed_extensions: list, max_size_mb: int):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File không được để trống hoặc không có tên.")
    parts = file.filename.rsplit(".", 1)
    ext = f".{parts[1].lower()}" if len(parts) > 1 else ""
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Định dạng file không hợp lệ. Chỉ chấp nhận: {allowed_extensions}")
    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)
    if size_bytes == 0:
        raise HTTPException(status_code=400, detail="File không được rỗng.")
    max_size_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_size_bytes:
        raise HTTPException(status_code=400, detail=f"Kích thước file vượt quá giới hạn ({max_size_mb} MB).")
    return size_bytes, ext
def generate_safe_filename(student_id: str, assignment_id: int, attempt: int, ext: str):
    unique_hash = uuid.uuid4().hex[:4]
    return f"{student_id}_assignment_{assignment_id}_attempt_{attempt}_{unique_hash}{ext}"
def save_file_safely(file: UploadFile, student_id: str, assignment_id: int, filename: str):
    dir_path = os.path.join(STORAGE_BASE, f"assignment_{assignment_id}", student_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Đã có lỗi xảy ra trong quá trình lưu file.")
    return file_path