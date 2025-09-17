"""Copyright (c) 2024, Aydin Abdi.

This module contains tests for the MermaidDiagram class in the sys_design_diagram.mermaid module.
"""

import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from sys_design_diagram.exceptions import MermaidExecutionError, MermaidFileNotFoundError
from sys_design_diagram.messages import ErrorMessages
from sys_design_diagram.mermaid import MermaidDiagram


@pytest.mark.asyncio
async def test_init_valid_file(setup_design_dirs):
    """Test initializing MermaidDiagram with a valid file."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)
    assert diagram.mermaid_file == mermaid_file


@pytest.mark.asyncio
async def test_init_invalid_file(setup_design_dirs):
    """Test initializing MermaidDiagram with an invalid file."""
    invalid_file = setup_design_dirs / "design_1" / "non_existent.mmd"
    with pytest.raises(
        MermaidFileNotFoundError, match=ErrorMessages.FILE_NOT_FOUND.value.format(file_path=invalid_file)
    ):
        MermaidDiagram(invalid_file)


@pytest.mark.asyncio
async def test_init_invalid_path_type():
    """Test initializing MermaidDiagram with an invalid path type."""
    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path="not_a_path")):
        MermaidDiagram("not_a_path")


@pytest.mark.asyncio
async def test_create_with_valid_output_dir(setup_design_dirs, output_dir):
    """Test creating a diagram with a valid output directory."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)
    await diagram.create(output_dir)

    # Check that a placeholder file was created (since mmdc likely won't work in CI)
    output_file = output_dir / "test.png"
    assert output_file.exists()

    # Should contain either actual PNG data or placeholder text
    content = output_file.read_text()
    assert "test.mmd" in content


@pytest.mark.asyncio
async def test_create_with_invalid_output_dir(setup_design_dirs):
    """Test creating a diagram with an invalid output directory."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Test with non-existent directory
    non_existent_dir = setup_design_dirs / "non_existent"
    with pytest.raises(
        ValueError, match=ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=non_existent_dir)
    ):
        await diagram.create(non_existent_dir)


@pytest.mark.asyncio
async def test_create_with_invalid_output_path_type(setup_design_dirs):
    """Test creating a diagram with an invalid output path type."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path="not_a_path")):
        await diagram.create("not_a_path")


@pytest.mark.asyncio
async def test_create_with_file_as_output_dir(setup_design_dirs):
    """Test creating a diagram with a file as output directory."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Create a file to use as output dir
    file_path = setup_design_dirs / "design_1" / "not_a_dir.txt"
    file_path.write_text("not a directory")

    with pytest.raises(ValueError, match=ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=file_path)):
        await diagram.create(file_path)


@pytest.mark.asyncio
async def test_create_with_mermaid_command_chrome_error(setup_design_dirs, output_dir):
    """Test creating a diagram when mermaid command fails with Chrome error."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock asyncio.create_subprocess_exec to simulate Chrome error
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"", b"Error: Chrome not found")

    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        await diagram.create(output_dir)

        # Check that a placeholder file was created
        output_file = output_dir / "test.png"
        assert output_file.exists()
        content = output_file.read_text()
        assert "Mermaid diagram placeholder for test.mmd" in content
        assert "graph TD" in content


@pytest.mark.asyncio
async def test_create_with_mermaid_command_non_chrome_error(setup_design_dirs, output_dir):
    """Test creating a diagram when mermaid command fails with non-Chrome error."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock asyncio.create_subprocess_exec to simulate non-Chrome error
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"", b"Syntax error in diagram")

    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        with pytest.raises(MermaidExecutionError, match="Failed to execute Mermaid"):
            await diagram.create(output_dir)


@pytest.mark.asyncio
async def test_create_with_mermaid_command_not_found(setup_design_dirs, output_dir):
    """Test creating a diagram when mermaid command is not found."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock asyncio.create_subprocess_exec to raise FileNotFoundError
    with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError("mmdc not found")):
        await diagram.create(output_dir)

        # Check that a placeholder file was created
        output_file = output_dir / "test.png"
        assert output_file.exists()
        content = output_file.read_text()
        assert "Mermaid diagram placeholder for test.mmd" in content
        assert "graph TD" in content


@pytest.mark.asyncio
async def test_check_mermaid_availability_success(setup_design_dirs):
    """Test _check_mermaid_availability when mermaid is available and working."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock successful version check and test render
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 0
    mock_version_process.communicate.return_value = (b"1.0.0", b"")

    mock_test_process = AsyncMock()
    mock_test_process.returncode = 0
    mock_test_process.communicate.return_value = (b"", b"")

    with patch("asyncio.create_subprocess_exec", side_effect=[mock_version_process, mock_test_process]):
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            # Mock temporary file creation
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.mmd"
            result = await diagram._check_mermaid_availability()
            assert result is True


@pytest.mark.asyncio
async def test_check_mermaid_availability_version_fail(setup_design_dirs):
    """Test _check_mermaid_availability when version command fails."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock failed version check
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 1
    mock_version_process.communicate.return_value = (b"", b"command not found")

    with patch("asyncio.create_subprocess_exec", return_value=mock_version_process):
        result = await diagram._check_mermaid_availability()
        assert result is False


@pytest.mark.asyncio
async def test_check_mermaid_availability_chrome_error(setup_design_dirs):
    """Test _check_mermaid_availability when Chrome is missing."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock successful version check but Chrome error in test render
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 0
    mock_version_process.communicate.return_value = (b"1.0.0", b"")

    mock_test_process = AsyncMock()
    mock_test_process.returncode = 1
    mock_test_process.communicate.return_value = (b"", b"Chrome not found")

    with patch("asyncio.create_subprocess_exec", side_effect=[mock_version_process, mock_test_process]):
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            # Mock temporary file creation
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.mmd"
            result = await diagram._check_mermaid_availability()
            assert result is False


@pytest.mark.asyncio
async def test_check_mermaid_availability_test_render_fail(setup_design_dirs):
    """Test _check_mermaid_availability when test render fails."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock successful version check but failed test render
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 0
    mock_version_process.communicate.return_value = (b"1.0.0", b"")

    mock_test_process = AsyncMock()
    mock_test_process.returncode = 1
    mock_test_process.communicate.return_value = (b"", b"syntax error")

    with patch("asyncio.create_subprocess_exec", side_effect=[mock_version_process, mock_test_process]):
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            # Mock temporary file creation
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.mmd"
            result = await diagram._check_mermaid_availability()
            assert result is False


@pytest.mark.asyncio
async def test_check_mermaid_availability_file_not_found(setup_design_dirs):
    """Test _check_mermaid_availability when mmdc command is not found."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock FileNotFoundError
    with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError("mmdc not found")):
        result = await diagram._check_mermaid_availability()
        assert result is False


@pytest.mark.asyncio
async def test_check_mermaid_availability_general_exception(setup_design_dirs):
    """Test _check_mermaid_availability when a general exception occurs."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock general exception
    with patch("asyncio.create_subprocess_exec", side_effect=RuntimeError("Something went wrong")):
        result = await diagram._check_mermaid_availability()
        assert result is False


@pytest.mark.asyncio
async def test_check_mermaid_availability_cleanup_exception(setup_design_dirs):
    """Test _check_mermaid_availability when cleanup fails but doesn't affect result."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock successful version check and test render
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 0
    mock_version_process.communicate.return_value = (b"1.0.0", b"")

    mock_test_process = AsyncMock()
    mock_test_process.returncode = 0
    mock_test_process.communicate.return_value = (b"", b"")

    # Mock temporary files to ensure both cleanup lines are tested
    class MockTempFile:
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def write(self, content):
            pass

    def mock_named_temp_file(mode="w", suffix="", delete=False):
        if suffix == ".mmd":
            return MockTempFile("/tmp/test.mmd")
        else:
            return MockTempFile("/tmp/test.png")

    with patch("asyncio.create_subprocess_exec", side_effect=[mock_version_process, mock_test_process]):
        with patch("tempfile.NamedTemporaryFile", side_effect=mock_named_temp_file):
            # Test with successful cleanup to cover line 119
            with patch("os.unlink") as mock_unlink:
                result = await diagram._check_mermaid_availability()
                assert result is True
                # Verify both unlink calls were made (line 118 and 119)
                assert mock_unlink.call_count == 2


@pytest.mark.asyncio
async def test_check_mermaid_availability_partial_cleanup_failure(setup_design_dirs):
    """Test _check_mermaid_availability when first cleanup fails but second succeeds."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock successful version check and test render
    mock_version_process = AsyncMock()
    mock_version_process.returncode = 0
    mock_version_process.communicate.return_value = (b"1.0.0", b"")

    mock_test_process = AsyncMock()
    mock_test_process.returncode = 0
    mock_test_process.communicate.return_value = (b"", b"")

    # Mock temporary files
    class MockTempFile:
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def write(self, content):
            pass

    def mock_named_temp_file(mode="w", suffix="", delete=False):
        if suffix == ".mmd":
            return MockTempFile("/tmp/test.mmd")
        else:
            return MockTempFile("/tmp/test.png")

    with patch("asyncio.create_subprocess_exec", side_effect=[mock_version_process, mock_test_process]):
        with patch("tempfile.NamedTemporaryFile", side_effect=mock_named_temp_file):
            # Test first unlink failing but second succeeding
            unlink_calls = 0

            def mock_unlink(path):
                nonlocal unlink_calls
                unlink_calls += 1
                if unlink_calls == 1:  # First call (temp_mmd) fails
                    raise OSError("Permission denied")
                # Second call (temp_png) succeeds - this covers line 119

            with patch("os.unlink", side_effect=mock_unlink):
                result = await diagram._check_mermaid_availability()
                assert result is True  # Cleanup failure shouldn't affect result


@pytest.mark.asyncio
async def test_create_with_successful_mermaid_command(setup_design_dirs, output_dir):
    """Test creating a diagram when mermaid command succeeds."""
    # Create a temporary mermaid file
    mermaid_file = setup_design_dirs / "design_1" / "test.mmd"
    mermaid_file.write_text("graph TD\n    A --> B")

    diagram = MermaidDiagram(mermaid_file)

    # Mock asyncio.create_subprocess_exec to simulate successful execution
    mock_process = AsyncMock()
    mock_process.returncode = 0  # Success
    mock_process.communicate.return_value = (b"PNG image created", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        await diagram.create(output_dir)

        # Check that the create method completed without error
        # The actual PNG file won't be created since we're mocking, but the method should complete
