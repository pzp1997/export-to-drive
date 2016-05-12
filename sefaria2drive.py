from __future__ import unicode_literals

import os

import requests
from oauth2client import client
from oauth2client import tools
import httplib2
import apiclient


def sefaria_sheet_api(sheet_id):
    """Gets JSON data of sheet with id `sheet_id` using the Sheet API"""
    BASE_URL = 'http://www.sefaria.org/api/sheets/'
    return requests.get('{}{}'.format(BASE_URL, sheet_id)).json()


def create_html_string(sheet):
    """Makes an html string from the JSON formatted sheet"""
    html = u''

    title = sheet.get('title', '').strip()
    title += '<br>' if len(title) > 0 else ''
    html += title

    for source in sheet['sources'][0:1]:
        try:
            text = source['text']
            # html += u'{}<br>{}'.format(
            #     text.get('en', ''),
            #     text.get('he', '').encode('utf-8'))
            html += text.get('en', '') + u'<br>'
        except KeyError:
            html += source.get('comment', '')
    return html


def create_html_file(sheet, path='files/'):
    """Creates an html file of `sheet` and returns path of its location."""
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, '{}.html'.format(sheet['id']))
    with open(file_path, 'w') as f:
        html_string = create_html_string(sheet)
        f.write(html_string)
    return file_path


class Store(object):
    """Stub class to get run_flow to work."""

    def put(self, credential):
        """Stub method that will be called in run_flow."""
        pass


def get_credentials(client_secrets='client_secrets.json',
                    scope_='https://www.googleapis.com/auth/drive',
                    redirect_uri_='http://localhost:8080'):
    """Authenticates the user with Google via OAuth 2.0"""
    flow = client.flow_from_clientsecrets(client_secrets,
                                          scope=scope_,
                                          redirect_uri=redirect_uri_)
    credentials = tools.run_flow(flow, Store(), None)
    return credentials


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)

    sheet_data = sefaria_sheet_api(raw_input("Input sheet id: "))

    file_metadata = {
        'name': sheet_data.get('title', '').strip(),
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    media = apiclient.http.MediaFileUpload(
                create_html_file(sheet_data),
                mimetype='text/html',
                resumable=True)

    new_file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id,webViewLink').execute()

    print '{} (id: {})'.format(new_file['webViewLink'], new_file['id'])


if __name__ == '__main__':
    main()
