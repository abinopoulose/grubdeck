# Data models for GrubDeck

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Theme:
    """Represents a GRUB theme with its metadata"""
    name: str
    description: str
    repo_link: str
    author: Optional[str] = None
    version: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.name:
            raise ValueError("Theme name is required")
        if not self.repo_link:
            raise ValueError("Theme repository link is required")


@dataclass
class ThemeInstallationResult:
    """Represents the result of a theme installation"""
    success: bool
    message: str
    theme_name: str
    
    def __post_init__(self):
        """Validate required fields"""
        if not isinstance(self.success, bool):
            raise ValueError("Success must be a boolean")
        if not self.message:
            raise ValueError("Message is required")
        if not self.theme_name:
            raise ValueError("Theme name is required")


@dataclass
class InstallationProgress:
    """Represents installation progress information"""
    percentage: int
    message: str
    
    def __post_init__(self):
        """Validate percentage range"""
        if not 0 <= self.percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        if not self.message:
            raise ValueError("Message is required")


@dataclass
class CarouselImage:
    """Represents an image in the carousel"""
    path: str
    name: str
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.path:
            raise ValueError("Image path is required")
        if not self.name:
            raise ValueError("Image name is required")
