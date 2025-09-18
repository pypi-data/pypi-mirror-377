"""
Lineage Versioning Example for DataLineagePy
Demonstrates saving, listing, diffing, and rolling back lineage graph versions.
"""
from datalineagepy.core.tracker import LineageTracker
from datalineagepy.core.lineage_versioning import LineageVersionManager

# Create tracker and version manager
tracker = LineageTracker(name="versioning_demo")
version_mgr = LineageVersionManager()

# Simulate some lineage changes
tracker.create_node("data", "dataset_v1")
version_mgr.save_version(tracker.export_graph())

tracker.create_node("data", "dataset_v2")
version_mgr.save_version(tracker.export_graph())

tracker.create_node("data", "dataset_v3")
version_mgr.save_version(tracker.export_graph())

# List versions
print("Available versions:", version_mgr.list_versions())

# Diff versions
print("Diff v1 to v3:", version_mgr.diff_versions(0, 2))

# Rollback to version 1
restored = version_mgr.rollback(0)
print("Rolled back to version 1. Node names:",
      [n['name'] for n in restored['nodes']])
