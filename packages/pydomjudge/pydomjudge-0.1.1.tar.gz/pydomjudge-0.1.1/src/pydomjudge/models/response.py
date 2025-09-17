from typing import List, Dict, Union
from pydantic import BaseModel

from pydomjudge.models.main import ContestState


class AccessInformation(BaseModel):
    """
    Represents access information for a user, including capabilities and endpoints.
    """
    capabilities: List[str]
    endpoints: List[Dict]  # Simplified for brevity

class ScoreboardRowProblem(BaseModel):
    """
    Represents a problem entry in a scoreboard row.
    """
    label: str
    solved: bool
    time: int

class ScoreboardRow(BaseModel):
    """
    Represents a row in the scoreboard, including rank, team, score, and problems.
    """
    rank: int
    team_id: str
    score: Dict[str, Union[int, float]]  # {"num_solved": 3, "total_time": 300}
    problems: List[ScoreboardRowProblem]

class Scoreboard(BaseModel):
    """
    Represents the contest scoreboard, including event, state, and rows.
    """
    event_id: str
    state: ContestState
    rows: List[ScoreboardRow]
