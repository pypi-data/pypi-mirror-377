"""
DataGuild Common Metadata Schemas

Common metadata structures shared across different entity types including
siblings relationships, ownership, and other cross-cutting concerns.

Author: DataGuild Engineering Team
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


@dataclass(frozen=True)
class Siblings:
    """
    Represents sibling relationships between entities.

    Used to establish relationships between entities that represent
    the same logical concept but exist in different contexts
    (e.g., shared databases, replicated tables).
    """

    primary: bool
    siblings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate siblings configuration."""
        if not isinstance(self.siblings, list):
            raise ValueError("Siblings must be a list of URNs")

        # Ensure siblings are unique
        if len(self.siblings) != len(set(self.siblings)):
            raise ValueError("Duplicate siblings are not allowed")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "primary": self.primary,
            "siblings": sorted(self.siblings)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Siblings':
        """Create instance from dictionary."""
        return cls(
            primary=data.get("primary", False),
            siblings=data.get("siblings", [])
        )

    def add_sibling(self, sibling_urn: str) -> 'Siblings':
        """Add a sibling URN (returns new instance due to frozen dataclass)."""
        if sibling_urn not in self.siblings:
            return Siblings(
                primary=self.primary,
                siblings=sorted(self.siblings + [sibling_urn])
            )
        return self

    def remove_sibling(self, sibling_urn: str) -> 'Siblings':
        """Remove a sibling URN (returns new instance due to frozen dataclass)."""
        new_siblings = [s for s in self.siblings if s != sibling_urn]
        return Siblings(primary=self.primary, siblings=new_siblings)

    def get_sibling_count(self) -> int:
        """Get the number of siblings."""
        return len(self.siblings)

    def has_sibling(self, sibling_urn: str) -> bool:
        """Check if a specific sibling exists."""
        return sibling_urn in self.siblings

    def __len__(self) -> int:
        """Get the number of siblings."""
        return len(self.siblings)

    def __contains__(self, sibling_urn: str) -> bool:
        """Check if sibling URN is in siblings list."""
        return sibling_urn in self.siblings


@dataclass(frozen=True)
class AuditStamp:
    """Represents audit information for metadata changes."""

    time: int  # Unix timestamp in milliseconds
    actor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"time": self.time}
        if self.actor:
            result["actor"] = self.actor
        return result

    @classmethod
    def now(cls, actor: Optional[str] = None) -> 'AuditStamp':
        """Create audit stamp for current time."""
        return cls(time=int(datetime.now().timestamp() * 1000), actor=actor)


@dataclass(frozen=True)
class Status:
    """Entity status information."""

    removed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {"removed": self.removed}


@dataclass(frozen=True)
class GlobalTags:
    """Global tags applied to entities."""

    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {"tags": sorted(self.tags)}

    def get_tag_count(self) -> int:
        """Get the number of tags."""
        return len(self.tags)


# Export all classes
__all__ = [
    'Siblings',
    'AuditStamp',
    'Status',
    'GlobalTags',
]
