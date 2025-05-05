import pytest
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_environment():
    # Setup
    os.environ["TESTING"] = "1"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]

@pytest.fixture
def test_file():
    content = "This is a test document for testing purposes."
    file_path = Path("test_uploads") / "test_file.docx"
    file_path.parent.mkdir(exist_ok=True)
    file_path.write_text(content)
    
    yield file_path
    
    # Cleanup
    if file_path.exists():
        file_path.unlink() 