"""
contains dataclasses for legacy add-on meta (BlInfo) and the blender_manifest.toml
"""

from dataclasses import dataclass


@dataclass
class BlInfo:
    name: str
    author: str
    version: tuple[int, ...]
    blender: tuple[int, ...]
    location: str
    description: str
    warning: str
    doc_url: str
    tracker_url: str
    category: str
    support: str
