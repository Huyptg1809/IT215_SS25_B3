from typing import Optional
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from datetime import datetime
from app.services import (
    validate_student_data,
    validate_assignment,
    check_attempt,
    validate_file,
    generate_safe_filename,
    save_file_safely,
    submissions_db
)
import uvicorn
app = FastAPI(title="Hệ thống Nộp Bài Tập Trực Tuyến")
@app.post("/api/v1/submissions")
async def submit_assignment(
    student_id: str = Form(...),
    student_name: str = Form(...),
    assignment_id: int = Form(...),
    note: Optional[str] = Form(None),
    submission_file: UploadFile = File(...)
):
    valid_student_id, valid_student_name = validate_student_data(student_id, student_name)
    assignment = validate_assignment(assignment_id)
    attempt = check_attempt(valid_student_id, assignment_id)
    file_size, ext = validate_file(
        submission_file, 
        assignment["allowed_extensions"], 
        assignment["max_size_mb"]
    )
    safe_filename = generate_safe_filename(valid_student_id, assignment_id, attempt, ext)
    save_file_safely(submission_file, valid_student_id, assignment_id, safe_filename)
    now_str = datetime.now().isoformat()
    submission_record = {
        "student_id": valid_student_id,
        "assignment_id": assignment_id,
        "attempt": attempt,
        "original_filename": submission_file.filename,
        "stored_filename": safe_filename,
        "file_size": file_size,
        "submitted_at": now_str
    }
    submissions_db.append(submission_record)
    return {
        "success": True,
        "message": "Submission uploaded successfully",
        "data": submission_record
    }
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)