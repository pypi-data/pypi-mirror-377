import json
import logging
import math
import os
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Literal

import requests
from fitrequest.client import FitRequest

from skillcorner_on_demand.method import METHOD_DOCSTRING, METHODS_BINDING

logger = logging.getLogger(__name__)

BASE_URL = 'https://tactical.skillcorner.com'
BASE_CLIENT_NAME = 'skillcorner_on_demand'
USERNAME = os.getenv('SKILLCORNER_ON_DEMAND_USERNAME')
PASSWORD = os.getenv('SKILLCORNER_ON_DEMAND_PASSWORD')


class PreservingFile:
    def __init__(self, file_object):
        self.file_object = file_object
        self._content = None

    def read(self, *args, **kwargs):
        if self._content is None:
            current_pos = self.file_object.tell()
            self.file_object.seek(0)
            self._content = self.file_object.read()
            self.file_object.seek(current_pos)
        return BytesIO(self._content).read(*args, **kwargs)


class SkillcornerOnDemandClient(FitRequest):
    """Client for the Skillcorner On Demand API."""

    base_url = BASE_URL
    base_client_name = BASE_CLIENT_NAME
    _docstring_template = METHOD_DOCSTRING
    _methods_binding = METHODS_BINDING

    def _check_request(self, method, url, **kwargs):
        kwargs_copy = kwargs.copy()
        if 'files' in kwargs_copy:
            preserving_files = {
                k: (v[0], PreservingFile(v[1]), v[2])
                for k, v in kwargs_copy['files'].items()
            }
            kwargs_copy['files'] = preserving_files
        super()._check_request(method, url, **kwargs_copy)

    def upload_match_video(
        self, match_id: int, path: str, is_update: bool = False
    ) -> dict:
        """Upload a video file to the server.

        Args:
            match_id (int): The match id.
            video_path (string): The path to the video file.
            is_update (bool): Whether to update the video file.

        Returns:
            string: The response from the server.

        Examples:
        ```py
            client.upload_match_video(1, 'path/to/my/video.mp4')
            # {'status': 201}
        ```

        """
        try:
            video_parts = self._get_number_of_parts(path)
            presigned_urls, upload_id = self._request_presigned_urls(
                match_id, video_parts, is_update
            )
            parts = self._multipart_upload(presigned_urls, path)
            return self.complete_multipart_upload(match_id, parts, upload_id, is_update)
        except Exception as e:
            return e

    def _request_presigned_urls(
        self, match_id: int, parts: int, is_update: bool = False
    ) -> tuple[list[str], str]:
        if is_update:
            res = self.session.put(
                self.base_url + f'/api/request/{match_id}/video/',
                json={'parts': parts},
                headers=self.session.headers,
            )
        else:
            res = self.session.post(
                self.base_url + f'/api/request/{match_id}/video/',
                json={'parts': parts},
                headers=self.session.headers,
            )
        return res.json()['presignedUrls'], res.json()['uploadId']

    def _multipart_upload(
        self, presigned_urls: list[str], video_path: Path
    ) -> list[dict]:
        part_size = 50 * 1024 * 1024
        parts = []
        print('Uploading video to the server...')
        with open(video_path, 'rb') as video_file:
            for i, presigned_url in enumerate(presigned_urls):
                video_chunk = video_file.read(part_size)
                etag = self._upload_part(presigned_url, video_chunk)
                parts.append({'PartNumber': i + 1, 'ETag': etag})
                print(f'Uploaded part {i + 1} / {len(presigned_urls)}')
        return parts

    def _upload_part(self, presigned_url: str, video_chunk) -> str:
        res = requests.put(presigned_url, data=video_chunk)
        res.raise_for_status()
        etag = res.headers['ETag']
        if not etag:
            raise ValueError(f'ETag not found in response headers: {res.headers}')
        return etag

    def complete_multipart_upload(
        self,
        match_id: int,
        parts: list[dict],
        upload_id: int,
        is_update: bool = False,
    ) -> requests.Response:
        if is_update:
            res = self.session.put(
                self.base_url + f'/api/request/{match_id}/video/',
                json={'parts': parts, 'complete': True, 'uploadId': upload_id},
                headers=self.session.headers,
            )
        else:
            res = self.session.post(
                self.base_url + f'/api/request/{match_id}/video/',
                json={'parts': parts, 'complete': True, 'uploadId': upload_id},
                headers=self.session.headers,
            )
        return res

    def _get_number_of_parts(self, video_path):
        file_size = os.path.getsize(video_path)
        return math.ceil(file_size / (50 * 1024 * 1024))

    def upload_match_sheet(self, match_id: int, path: str, is_update: bool = False):
        """Post a match sheet to the server.

        Args:
            match_id (int): The match id.
            match_sheet (dict): Path of the file.
            is_update (bool): Whether to update the match sheet.

        Returns:
            dict: The response from the server.

        Examples:
        ```py
            response = client.post_match_sheet(1, 'path/to/my/file.csv')
            # {"message": "Information successfully added to the request"}
        ```

        """
        with open(path, 'rb') as match_sheet_file:
            try:
                if is_update:
                    return self.update_match_sheet(
                        match_id,
                        files={
                            'file': (
                                'match_sheet.csv',
                                match_sheet_file,
                                'text/csv',
                            )
                        },
                    )
            except Exception as e:
                return e
            try:
                return self.post_match_sheet(
                    match_id,
                    files={'file': ('match_sheet.csv', match_sheet_file, 'text/csv')},
                )
            except Exception as e:
                return e

    def upload_period_limits(self, match_id: int, path: str, is_update: bool = False):
        """Post period limits to the server.

        Args:
            match_id (int): The match id.
            period_limits_path (string): The path to the period limits file.
            is_update (bool): Whether to update the period limits.

        Returns:
            dict: The response from the server.

        Examples:
        ```py
            response = client.upload_period_limits(1, 'path/to/my/file.csv')
            # {"message": "Information successfully added and uploaded to the request"}
        ```
        """
        with open(path, 'rb') as period_limits_file:
            try:
                if is_update:
                    return self.update_period_limits(
                        match_id,
                        files={
                            'file': (
                                'period_limits.csv',
                                period_limits_file,
                                'text/csv',
                            )
                        },
                    )
            except Exception as e:
                return e

            try:
                return self.post_period_limits(
                    match_id,
                    files={
                        'file': ('period_limits.csv', period_limits_file, 'text/csv')
                    },
                )
            except Exception as e:
                return e

    def upload_home_team_side(self, match_id: int, path: int, is_update: bool = False):
        """Post home team side to the server.

        Args:
            match_id (int): The match id.
            home_team_side_path (string): The path to the home team side file.
            is_update (bool): Whether to update the home team side.

        Returns:
            dict: The response from the server.

        Examples:
        ```py
            response = client.upload_home_team_side(1, 'path/to/my/file.csv')
            # {'message': 'Home Team Side successfully added and uploaded to the request'}
        ```
        """
        with open(path, 'rb') as home_team_side_file:
            try:
                if is_update:
                    return self.update_home_team_side(
                        match_id,
                        files={
                            'file': (
                                'home_team_side.csv',
                                home_team_side_file,
                                'text/csv',
                            )
                        },
                    )
            except Exception as e:
                return e

            try:
                return self.post_home_team_side(
                    match_id,
                    files={
                        'file': ('home_team_side.csv', home_team_side_file, 'text/csv')
                    },
                )
            except Exception as e:
                return e

    def get_match_physical(self, match_id: int, csv: bool = False):
        """Get the physical data of a match.

        Args:
            match_id (int): The match id.
            csv (bool): Whether to return the response as a CSV file.

        Returns:
            dict or file: The response from the server.

        Examples:
        ```py
            response = client.get_match_physical(match_id=1234556, csv=True)
            # CSV file or bytes response
        ```
        """
        try:
            physical_data = self.get_physical(match_id)
            if csv:
                with open(f'match_{match_id}_physical_data.csv', 'wb') as f:
                    f.write(physical_data)
                return f'match_{match_id}_physical_data.csv'
            return physical_data
        except Exception as e:
            return e

    def launch_match(self, match_id: int) -> dict:
        """Launch a match.

        Args:
            match_id (int): The match id.

        Returns:
            dict: The response from the server.s

        Examples:
        ```py
            response = client.launch_match(match_id=1)
            # {'message': 'Match added to processing queue'}
        ```
        """
        try:
            return self.post_launch_match(match_id)
        except Exception as e:
            return e

    def get_tracking(self, match_id: int):
        """Get the tracking data of a match and save it to a file.
        Warning: This method can take a long time to complete because of the large file size.
        Args:
            match_id (int): The match id.

        Returns:
            str: The name of the tracking data file.

        Examples:
        ```py
            response = client.get_tracking(match_id=1234567)
            # 'match_1234567_tracking_data.jsonl'
        ```
        """
        try:
            presigned_url = self.get_tracking_data(match_id)
            res = requests.get(presigned_url['url'])
            res.raise_for_status()
            with open(f'match_{match_id}_tracking_data.jsonl', 'wb') as f:
                f.write(res.content)
            return f'match_{match_id}_tracking_data.jsonl'
        except Exception as e:
            return e

    def get_data_collection(self, match_id: int):
        """Get the data collection of a match.
        Args:
            match_id (int): The match id.
        Returns:
            dict: The response from the server.
        """
        try:
            return self.data_collection(match_id)
        except Exception as e:
            return e

    def get_match_data(self, match_id: int):
        """Get the match data of a match.
        Args:
            match_id (int): The match id.
        Returns:
            dict: The response from the server.
        """
        try:
            return self.match_data(match_id)
        except Exception as e:
            return e

    def upload_match_list(self, path: str):
        """Post a match list to the server.
        Args:
            path (str): The path to the match list file.
        Returns:
            dict: The response from the server.
        """
        try:
            with open(path, 'rb') as f:
                print(Path(path).name)
                return self.post_match_list(
                    files={
                        'file': (
                            Path(path).name,
                            f,
                            'text/csv',
                        ),
                    }
                )
        except Exception as e:
            return e

    def get_dynamic_events(
        self,
        match_id: int,
        file_format: Literal[
            'csv', 'sportscode-xml', 'matchtracker-xml', 'focus-json'
        ] = 'csv',
        save: bool = True,
    ):
        """Get the dynamic events of a match and save it to a file.

        Args:
            match_id (int): The match id.
            file_format (str): The format of the file to download.
            save (bool): Whether to save the response to a file.

        Returns:
            str or bytes: The filename if saved, otherwise the raw response.

        Examples:
        ```py
            response = client.get_dynamic_events(match_id=1234567, file_format='csv')
            # 'match_1234567_dynamic_events.csv'
        ```
        """
        try:
            response = self.get_match_dynamic_events(
                match_id, params={'file_format': file_format}
            )

            if save:
                extension_map = {
                    'csv': '.csv',
                    'sportscode-xml': '_sportscode.xml',
                    'matchtracker-xml': '_matchtracker.xml',
                    'focus-json': '_focus.json',
                }
                extension = extension_map.get(file_format, 'txt')
                filename = f'match_{match_id}_dynamic_events{extension}'

                with open(filename, 'wb') as f:
                    if hasattr(response, 'tag'):
                        content = ET.tostring(
                            response, encoding='utf-8', xml_declaration=True
                        )
                        f.write(content)
                    elif isinstance(response, (str, bytes)):
                        content = (
                            response.encode('utf-8')
                            if isinstance(response, str)
                            else response
                        )
                        f.write(content)
                    else:
                        content = json.dumps(response, indent=2).encode('utf-8')
                        f.write(content)
                return filename

            return response
        except Exception as e:
            return e
