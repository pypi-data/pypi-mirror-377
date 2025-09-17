from io import BytesIO

import pytest
from requests_mock import Mocker

from src.skillcorner_on_demand.client import (
    PreservingFile,
    SkillcornerOnDemandClient,
)


@pytest.fixture
def client():
    return SkillcornerOnDemandClient(username='test_user', password='test_pass')


@pytest.fixture
def mock_video_file(tmp_path):
    video_path = tmp_path / 'test_video.mp4'
    video_path.write_bytes(b'0' * 1024 * 1024 * 115)
    return video_path


def test_preserving_file():
    content = b'test content'
    file_obj = BytesIO(content)
    preserving_file = PreservingFile(file_obj)

    assert preserving_file.read() == content


def test_request_presigned_urls(client, requests_mock: Mocker):
    match_id = 123
    parts = 2
    expected_urls = ['url1', 'url2']

    requests_mock.post(
        'https://tactical.skillcorner.com/api/request/123/video/',
        json={'presignedUrls': expected_urls, 'uploadId': 1},
    )

    result = client._request_presigned_urls(match_id, parts)

    assert result[0] == expected_urls
    assert result[1] == 1


def test_multipart_upload(client, mock_video_file, requests_mock: Mocker):
    presigned_urls = ['https://example.com/upload/1', 'https://example.com/upload/2']

    requests_mock.put('https://example.com/upload/1', headers={'ETag': 'etag1'})
    requests_mock.put('https://example.com/upload/2', headers={'ETag': 'etag2'})

    result = client._multipart_upload(presigned_urls, mock_video_file)

    assert result == [
        {'PartNumber': 1, 'ETag': 'etag1'},
        {'PartNumber': 2, 'ETag': 'etag2'},
    ]


def test_upload_part(client, requests_mock: Mocker):
    presigned_url = 'https://example.com/upload'
    video_chunk = b'test_chunk'
    expected_etag = 'test_etag'

    requests_mock.put(presigned_url, headers={'ETag': expected_etag})

    result = client._upload_part(presigned_url, video_chunk)

    assert result == expected_etag


def test_complete_multipart_upload(client, requests_mock: Mocker):
    match_id = 123
    parts = [{'partNumber': 1, 'ETag': 'etag1'}, {'partNumber': 2, 'ETag': 'etag2'}]

    requests_mock.post(
        'https://tactical.skillcorner.com/api/request/123/video/',
        json={'status': 'success'},
    )

    result = client.complete_multipart_upload(match_id, parts, upload_id=1)

    assert result.json() == {'status': 'success'}


def test_get_number_of_parts(client, mock_video_file):
    result = client._get_number_of_parts(mock_video_file)
    assert result == 3  # 50 MB file divided into 3 parts
