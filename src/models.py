from dataclasses import dataclass, field
from typing import List

@dataclass
class Theme:
    """Represents a single GRUB theme with all its metadata."""
    id: int
    name: str
    cover_image: str
    repo_link: str
    description: str
    created_by: str
    carousel_images: List[str] = field(default_factory=list)
