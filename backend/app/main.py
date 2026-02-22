from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Pattern, Upload
from .patterns import extract_patterns
from .schemas import PatternRead, UploadCreateResponse, UploadPatternRead, UploadPatternsResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LogLens API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadCreateResponse)
async def upload_log(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadCreateResponse:
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="replace")

    upload = Upload(filename=file.filename or "uploaded.log", raw_text=text)
    db.add(upload)
    db.flush()

    extracted_patterns = extract_patterns(text)
    for item in extracted_patterns:
        db.add(
            Pattern(
                upload_id=upload.id,
                pattern_text=str(item["pattern_text"]),
                count=int(item["count"]),
                sample_line=str(item["sample_line"]),
            )
        )

    db.commit()
    db.refresh(upload)
    return UploadCreateResponse(
        id=upload.id,
        filename=upload.filename,
        pattern_count=len(extracted_patterns),
    )


@app.get("/api/uploads/{id}/patterns", response_model=UploadPatternsResponse)
def list_upload_patterns(id: int, db: Session = Depends(get_db)) -> UploadPatternsResponse:
    upload = db.query(Upload).filter(Upload.id == id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    previous_pattern_rows = db.execute(
        select(Pattern.pattern_text)
        .join(Upload, Pattern.upload_id == Upload.id)
        .where(Upload.id < upload.id)
        .distinct()
    ).all()
    previous_patterns = {row[0] for row in previous_pattern_rows}

    upload_patterns = [
        UploadPatternRead(
            id=pattern.id,
            upload_id=pattern.upload_id,
            pattern_text=pattern.pattern_text,
            count=pattern.count,
            sample_line=pattern.sample_line,
            is_new=pattern.pattern_text not in previous_patterns,
        )
        for pattern in upload.patterns
    ]

    return UploadPatternsResponse(
        id=upload.id,
        filename=upload.filename,
        created_at=upload.created_at,
        patterns=upload_patterns,
    )


@app.get("/api/patterns/{id}", response_model=PatternRead)
def get_pattern(id: int, db: Session = Depends(get_db)) -> PatternRead:
    pattern = db.query(Pattern).filter(Pattern.id == id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return PatternRead.model_validate(pattern)
