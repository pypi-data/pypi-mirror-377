import os
import json
import sys

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_filesystem_extra.server import FilesystemExtraServer

@pytest.fixture
def setup_environment():
    """Fixture to set up environment variables and temporary directories."""
    temp_dir = TemporaryDirectory()  # Create a temporary directory
    os.environ["PROJECT_BOOTSTRAP"] = temp_dir.name
    os.environ["ALLOWED_DIR"] = temp_dir.name

    yield temp_dir.name  # Provide the temporary directory to the tests

    # Teardown: Cleanup temporary directory
    temp_dir.cleanup()
    del os.environ["PROJECT_BOOTSTRAP"]
    del os.environ["ALLOWED_DIR"]

@pytest.fixture
def multiline_file(setup_environment):
    """Fixture to set up environment variables and temporary directories."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "lines_file.txt"
    file_content = """Line one
    Line two
    Line three"""
    file_path.write_text(file_content)
    return str(file_path)

@pytest.mark.asyncio
async def test_search_files_by_regex(setup_environment):
    """Test reading a valid bootstrap file."""
    temp_dir = setup_environment
    file_content = "Hello, World!"

    wanted_file_path = Path(temp_dir) / "find_me_file.txt"
    wanted_file_path.write_text(file_content)

    unwanted_file_path = Path(temp_dir) / "hide_me_file.txt"
    unwanted_file_path.write_text(file_content)

    server = FilesystemExtraServer()
    args = {"path": temp_dir, "regex": "[fh]i.*_me_file[.]txt", "excludeRegexes": ["hide.*"]}
    result = await server.search_files_by_regex(args)

    assert len(result) == 1
    assert "find_me_file" in result[0].text
    assert "hide_me_file" not in result[0].text

@pytest.mark.asyncio
async def test_read_bootstrap_file_valid(setup_environment):
    """Test reading a valid bootstrap file."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.txt"
    file_content = "Hello, World!"
    file_path.write_text(file_content)

    server = FilesystemExtraServer()
    args = {"path": "test_file.txt"}
    result = await server.read_bootstrap_file(args)

    assert len(result) == 1
    assert result[0].text == file_content

@pytest.mark.asyncio
async def test_read_bootstrap_file_not_found(setup_environment):
    """Test reading a non-existent bootstrap file."""
    server = FilesystemExtraServer()
    args = {"path": "nonexistent.txt"}
    result = await server.read_bootstrap_file(args)

    assert len(result) == 1
    assert "No such file or directory" in result[0].text

@pytest.mark.asyncio
async def test_read_file_lines_middle(multiline_file):
    """Test reading file line ranges"""
    server = FilesystemExtraServer()
    args = {"path": multiline_file, "startLine": 1, "endLine": 2}
    result = await server.read_file_lines(args)

    assert len(result) == 1
    assert "Line one" in result[0].text
    assert "Line two" in result[0].text
    assert "Line three" not in result[0].text

@pytest.mark.asyncio
async def test_read_file_lines_from_start(multiline_file):
    """Test reading file line ranges"""
    server = FilesystemExtraServer()
    args = {"path": multiline_file, "endLine": 2}
    result = await server.read_file_lines(args)

    assert len(result) == 1
    assert "Line one" in result[0].text
    assert "Line two" in result[0].text
    assert "Line three" not in result[0].text

@pytest.mark.asyncio
async def test_read_file_lines_till_end(multiline_file):
    """Test reading file line ranges"""
    server = FilesystemExtraServer()
    args = {"path": multiline_file, "startLine": 2}
    result = await server.read_file_lines(args)

    assert len(result) == 1
    assert "Line one" not in result[0].text
    assert "Line two" in result[0].text
    assert "Line three" in result[0].text

@pytest.mark.asyncio
async def test_read_file_lines_out_of_range(multiline_file):
    """Test reading file line ranges"""
    server = FilesystemExtraServer()
    args = {"path": multiline_file, "startLine": 1, "endLine": 99}
    result = await server.read_file_lines(args)

    assert len(result) == 1
    assert "Invalid start or end line number" in result[0].text
    assert "must be between 1 and 3" in result[0].text

@pytest.mark.asyncio
async def test_append_file_create(setup_environment):
    """Test appending to a file that does not exist (create new file)."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.txt"

    server = FilesystemExtraServer()
    args = {"path": str(file_path), "content": "Hello, World!"}
    result = await server.append_file(args)

    assert len(result) == 1
    assert file_path.read_text() == "Hello, World!"

@pytest.mark.asyncio
async def test_append_file_existing(setup_environment):
    """Test appending to an existing file."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.txt"
    file_path.write_text("Hello")

    server = FilesystemExtraServer()
    args = {"path": str(file_path), "content": "World"}
    result = await server.append_file(args)

    assert len(result) == 1
    assert file_path.read_text() == "Hello\nWorld"

@pytest.mark.asyncio
async def test_append_structured_file_create(setup_environment):
    """Test appending structured data to a new file."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.json"
    content = {"key": "value"}

    server = FilesystemExtraServer()
    args = {"path": str(file_path), "content": json.dumps(content)}
    result = await server.append_structured_file(args)

    assert len(result) == 1
    assert json.loads(file_path.read_text()) == [content]

@pytest.mark.asyncio
async def test_append_structured_file_existing(setup_environment):
    """Test appending structured data to an existing file."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.json"
    initial_content = [{"key": "value1"}]
    file_path.write_text(json.dumps(initial_content))

    new_content = {"key": "value2"}
    server = FilesystemExtraServer()
    args = {"path": str(file_path), "content": json.dumps(new_content)}
    result = await server.append_structured_file(args)

    assert len(result) == 1
    assert json.loads(file_path.read_text()) == initial_content + [new_content]

@pytest.mark.asyncio
async def test_append_structured_file_invalid_json(setup_environment):
    """Test appending invalid JSON content to a structured file."""
    temp_dir = setup_environment
    file_path = Path(temp_dir) / "test_file.json"

    server = FilesystemExtraServer()
    args = {"path": str(file_path), "content": "invalid_json"}
    result = await server.append_structured_file(args)

    assert len(result) == 1
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_validate_path_outside_allowed_directory(setup_environment):
    """Test validation for a path outside the allowed directory."""
    temp_dir = setup_environment
    invalid_path = "/etc/passwd"

    server = FilesystemExtraServer()
    with pytest.raises(PermissionError, match="Access denied"):
        await server._validate_path(invalid_path)

@pytest.mark.asyncio
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Symlink creation is restricted on Windows platform")
async def test_validate_path_symlink_outside_allowed_directory(setup_environment):
    """Test validation for a symlink pointing outside the allowed directory."""
    temp_dir = setup_environment
    symlink_path = Path(temp_dir) / "symlink"
    target_path = Path("/etc/passwd")
    symlink_path.symlink_to(target_path)

    server = FilesystemExtraServer()
    with pytest.raises(PermissionError, match="Access denied"):
        await server._validate_path(str(symlink_path))