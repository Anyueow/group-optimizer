# models.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class LinkedInProfile:
    """
    Represents a LinkedIn profile's data fields.
    """

    name: str = ""
    followers: int = 0
    title: str = ""
    verified: bool = False
    experiences: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"<LinkedInProfile(name={self.name!r}, followers={self.followers}, "
            f"title={self.title!r}, verified={self.verified}, "
            f"experiences={self.experiences}, skills={self.skills})>"
        )
