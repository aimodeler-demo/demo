from pathlib import Path

def test_workflow_source_exists():
    assert (Path(__file__).resolve().parents[1] / "src" / "example_workflow" / "workflow.py").is_file()
