#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client",
#     "google-auth-httplib2",
#     "google-auth-oauthlib",
# ]
# ///

import argparse
import os.path
from io import BytesIO
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload


class GDriveClient:
    SCOPES = [
        "https://www.googleapis.com/auth/drive.file",
        #        'https://www.googleapis.com/auth/drive', # possibly
    ]

    def __init__(
        self, credentials_filename, server_port=59587, token_filename="token_gdrive.json"
    ):
        self.credentials_filename = credentials_filename
        self.server_port = server_port
        self.token_filename = token_filename
        self.credentials = self.authenticate()
        self.service = build("drive", "v3", credentials=self.credentials)

    def authenticate(self):
        credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_filename):
            credentials = Credentials.from_authorized_user_file(
                self.token_filename, self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                    self.credentials_filename,
                    self.SCOPES,
                )
                credentials = flow.run_local_server(port=self.server_port)
            # Save the credentials for the next run
            with open(self.token_filename, "w") as token:
                token.write(credentials.to_json())
        return credentials

    def upload_json(self, data, filename, folder_id=None, **kwargs):
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        dh = BytesIO(json.dumps(data).encode("utf-8"))
        media = MediaIoBaseUpload(dh, mimetype="application/json", resumable=True)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file["id"]

    def upload_jsonfile(
        self, filename, destination_filename=None, folder_id=None, **kwargs
    ):
        file_metadata = {
            "name": filename if destination_filename is None else destination_filename
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]
        media = MediaFileUpload(filename, mimetype="application/json", resumable=True)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file["id"]


parser = argparse.ArgumentParser(description="Upload json file to googledrive.")
parser.add_argument("json_file", type=str, help="File to upload.")
parser.add_argument(
    "--destination_filename",
    "-n",
    type=str,
    help="Name to give the file in google drive.",
)
parser.add_argument(
    "--folder_id",
    "-f",
    default=None,
    type=str,
    help="Folder ID where the file should be put, note this is _not_ the name of the folder.",
)
parser.add_argument(
    "--credentials_filename",
    default="gdrive_client_secret.json",
    type=str,
    help="A client credentials file.",
)


if __name__ == "__main__":
    args = parser.parse_args()
    drive = GDriveClient(args.credentials_filename)
    file_id = drive.upload_jsonfile(
        args.json_file,
        destination_filename=args.destination_filename,
        folder_id=args.folder_id,
    )
    print("uploaded file")
