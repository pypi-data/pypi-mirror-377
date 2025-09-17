from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from pydomjudge.models.shared import StatementFile, ImageFile, ArchiveFile


class User(BaseModel):
    """
    Represents a user in the system, including identity, team, roles, and status.
    """
    id: str
    username: str
    name: str
    email: Optional[str] = None
    team_id: Optional[str] = None
    roles: List[str]
    enabled: bool
    last_login_time: Optional[datetime] = None

class ContestState(BaseModel):
    """
    Tracks the timing and state changes of a contest.
    """
    started: Optional[datetime] = None
    ended: Optional[datetime] = None
    frozen: Optional[datetime] = None
    thawed: Optional[datetime] = None
    finalized: Optional[datetime] = None
    end_of_updates: Optional[datetime] = None

class ContestProblem(BaseModel):
    """
    Describes a contest problem, including its label, name, time limit, and statements.
    """
    id: str
    label: str
    name: str
    time_limit: float
    statement: List[StatementFile] = Field(default_factory=list)

class Balloon(BaseModel):
    """
    Represents a balloon awarded to a team for solving a problem in a contest.
    """
    balloonid: int
    time: str
    problem: str
    contestproblem: ContestProblem
    team: str
    teamid: int
    location: Optional[str]
    affiliation: Optional[str]
    affiliationid: Optional[int]
    category: str
    total: List[ContestProblem]
    awards: str
    done: bool

class Award(BaseModel):
    """
    Represents an award and its recipients in a contest.
    """
    id: str
    citation: str
    team_ids: List[str]

class Contest(BaseModel):
    """
    Contains contest metadata, timing, and banner images.
    """
    id: str
    name: str
    shortname: str
    start_time: datetime
    end_time: datetime
    banner: List[ImageFile] = Field(default_factory=list)  # From "Banner" schema

class ContestStatus(BaseModel):
    """
    Tracks the number of submissions, queued, and judging in a contest.
    """
    num_submissions: int
    num_queued: int
    num_judging: int

class Event(BaseModel):
    """
    Represents a system event, including type, operation, and data.
    """
    id: str
    type: str
    op: str
    data: Dict
    time: str

class Team(BaseModel):
    """
    Represents a team, including its name, display name, groups, and photos.
    """
    id: str
    name: str
    display_name: Optional[str] = None
    group_ids: List[str] = Field(default_factory=list)
    photo: List[ImageFile] = Field(default_factory=list)  # From "Photo" schema

class Submission(BaseModel):
    """
    Represents a team's submission, including files and metadata.
    """
    id: str
    language_id: str
    problem_id: str
    team_id: str
    time: datetime
    files: List[ArchiveFile] = Field(default_factory=list)  # From "Files" schema

class TeamCategory(BaseModel):
    """
    Represents a team category, including ICPC info and color.
    """
    id: str
    name: str
    hidden: bool
    icpc_id: str
    sortorder: int
    color: str

class JudgementType(BaseModel):
    """
    Represents a judgement type, including penalty and solved status.
    """
    id: str
    name: str
    penalty: bool
    solved: bool

class Judgehost(BaseModel):
    """
    Represents a judgehost, including hostname and status.
    """
    id: str
    hostname: str
    enabled: bool
    polltime: str
    hidden: bool

class Language(BaseModel):
    """
    Represents a programming language and its configuration for judging.
    """
    id: str
    name: str
    extensions: List[str]
    compile_executable_hash: Optional[str]
    filter_compiler_files: bool
    allow_judge: bool
    time_factor: float
    entry_point_required: bool
    entry_point_name: Optional[str]

class Judging(BaseModel):
    """
    Represents a judging process for a submission.
    """
    id: str
    submission_id: str
    start_time: str
    start_contest_time: str
    end_time: str
    end_contest_time: str
    valid: bool

class Judgement(BaseModel):
    """
    Represents a judgement for a submission, including type and validity.
    """
    id: str
    submission_id: str
    judgement_type_id: Optional[str] = None
    valid: bool
    max_run_time: Optional[float] = None

class TeamAffiliation(BaseModel):
    """
    Represents a team's affiliation, including ICPC and country info.
    """
    id: str
    shortname: str
    icpc_id: Optional[str]
    name: str
    formal_name: str
    country: Optional[str]

class Clarification(BaseModel):
    """
    Represents a clarification request or response in a contest.
    """
    id: str
    text: str
    problem_id: Optional[str] = None
    from_team_id: Optional[str] = None
    to_team_id: Optional[str] = None
    time: Optional[datetime] = None

class JudgingRun(BaseModel):
    """
    Represents a single run in a judging process for a submission.
    """
    id: str
    judgement_id: str
    run_time: float
    time: str
    contest_time: str
    ordinal: int
