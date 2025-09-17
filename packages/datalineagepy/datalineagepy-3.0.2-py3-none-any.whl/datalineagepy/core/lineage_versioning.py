"""
Lineage Versioning and Version Control for DataLineagePy
Provides versioning, rollback, and diff utilities for lineage graphs.
"""
from typing import Dict, Any, List, Optional
import copy
import datetime


class LineageVersionManager:
    """Manages versions of the lineage graph."""

    def __init__(self):
        self.versions: List[Dict[str, Any]] = []
        self.timestamps: List[str] = []
        self.current_version: int = -1

    def save_version(self, lineage_graph: Dict[str, Any]):
        """Save a new version of the lineage graph."""
        version = copy.deepcopy(lineage_graph)
        self.versions.append(version)
        self.timestamps.append(datetime.datetime.utcnow().isoformat())
        self.current_version = len(self.versions) - 1
        return self.current_version

    def get_version(self, version_index: int) -> Optional[Dict[str, Any]]:
        if 0 <= version_index < len(self.versions):
            return copy.deepcopy(self.versions[version_index])
        return None

    def list_versions(self) -> List[Dict[str, Any]]:
        return [
            {"version": i, "timestamp": self.timestamps[i]}
            for i in range(len(self.versions))
        ]

    def rollback(self, version_index: int) -> Optional[Dict[str, Any]]:
        if 0 <= version_index < len(self.versions):
            self.current_version = version_index
            return copy.deepcopy(self.versions[version_index])
        return None

    def diff_versions(self, v1: int, v2: int) -> Dict[str, Any]:
        """Return a simple diff between two versions (nodes/edges/operations count)."""
        ver1 = self.get_version(v1)
        ver2 = self.get_version(v2)
        if not ver1 or not ver2:
            return {"error": "Invalid version index"}
        diff = {
            "nodes_added": len(ver2.get("nodes", [])) - len(ver1.get("nodes", [])),
            "edges_added": len(ver2.get("edges", [])) - len(ver1.get("edges", [])),
            "operations_added": len(ver2.get("operations", [])) - len(ver1.get("operations", [])),
        }
        return diff
