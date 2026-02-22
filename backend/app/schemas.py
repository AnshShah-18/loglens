from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    upload_id: int
    pattern_text: str
    count: int
    sample_line: str


class UploadPatternRead(PatternRead):
    is_new: bool


class UploadCreateResponse(BaseModel):
    id: int
    filename: str
    pattern_count: int


class UploadPatternsResponse(BaseModel):
    id: int
    filename: str
    created_at: datetime
    patterns: list[UploadPatternRead]
