from typing import List, Optional, Dict
from pydantic import BaseModel


class ClarificationPost(BaseModel):
    """
    Represents a clarification post request for a contest.
    """
    text: str
    problem_id: Optional[str] = None
    reply_to_id: Optional[str] = None

class SubmissionRequest(BaseModel):
    """
    Represents a submission request, including problem, language, and files.
    """
    problem_id: str
    language_id: str
    files: List[Dict]  # Base64-encoded ZIP files
    entry_point: Optional[str] = None
