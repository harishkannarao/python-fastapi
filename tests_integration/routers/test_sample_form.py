import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

FILE_1_CONTENT = "Sample file to verify form upload\nAlso to verify download of file"
FILE_2_CONTENT = "Second file content"
FILE_1_PATH = "form_file_upload_1.txt"
FILE_2_PATH = "form_file_upload_2.txt"

FILE_UPLOAD_PATH = "/context/file-transfer/form-submit"
FILE_DOWNLOAD_PATH = "/context/file-transfer/files"


@pytest.fixture(autouse=True)
def setup_tear_down_fixture(test_client: TestClient) -> Generator[None, None, None]:
    # Setup: Ensure upload directory is clean
    target_file1_path: str = os.path.join(tempfile.gettempdir(), FILE_1_PATH)
    if os.path.exists(target_file1_path):
        os.remove(target_file1_path)
    target_file2_path: str = os.path.join(tempfile.gettempdir(), FILE_2_PATH)
    if os.path.exists(target_file2_path):
        os.remove(target_file2_path)

    # Setup: Clean up local test files
    if os.path.exists(FILE_1_PATH):
        os.remove(FILE_1_PATH)
    if os.path.exists(FILE_2_PATH):
        os.remove(FILE_2_PATH)

    # Create sample files for testing
    with open(FILE_1_PATH, "w") as f:
        f.write(FILE_1_CONTENT)
    with open(FILE_2_PATH, "w") as f:
        f.write(FILE_2_CONTENT)

    yield

    # Teardown: Clean up upload directory
    target_file1_path: str = os.path.join(tempfile.gettempdir(), FILE_1_PATH)
    if os.path.exists(target_file1_path):
        os.remove(target_file1_path)
    target_file2_path: str = os.path.join(tempfile.gettempdir(), FILE_2_PATH)
    if os.path.exists(target_file2_path):
        os.remove(target_file2_path)

    # Teardown: Clean up local test files
    if os.path.exists(FILE_1_PATH):
        os.remove(FILE_1_PATH)
    if os.path.exists(FILE_2_PATH):
        os.remove(FILE_2_PATH)


def test_file_upload_and_download(test_client: TestClient):
    with open(FILE_1_PATH, "rb") as f1, open(FILE_2_PATH, "rb") as f2:
        files = [
            ("files", (FILE_1_PATH, f1, "text/plain")),
            ("files", (FILE_2_PATH, f2, "text/plain")),
        ]
        data = {"firstName": "first", "lastName": "last"}
        response = test_client.post(
            FILE_UPLOAD_PATH, data=data, files=files, follow_redirects=False
        )

    assert response.status_code == 303

    download_file1 = test_client.get(f"{FILE_DOWNLOAD_PATH}/{FILE_1_PATH}")
    assert download_file1.status_code == 200
    assert download_file1.text == FILE_1_CONTENT

    download_file2 = test_client.get(f"{FILE_DOWNLOAD_PATH}/{FILE_2_PATH}")
    assert download_file2.status_code == 200
    assert download_file2.text == FILE_2_CONTENT
