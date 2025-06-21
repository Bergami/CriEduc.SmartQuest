from fastapi import UploadFile

def is_pdf(file: UploadFile) -> bool:
    file.file.seek(0)
    header = file.file.read(5)
    file.file.seek(0)
    return header == b"%PDF-"
