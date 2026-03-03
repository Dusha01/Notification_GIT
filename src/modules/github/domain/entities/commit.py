from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CommitAuthor:

    name: str
    email: str


@dataclass
class Commit:

    sha: str
    message: str
    author: CommitAuthor
    html_url: str
    branch: Optional[str] = None

    @property
    def sha_short(self) -> str:
        """Short SHA (7 chars)."""
        return self.sha[:7]
