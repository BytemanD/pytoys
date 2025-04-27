import dataclasses
import json
import re
from urllib import parse

from loguru import logger
import prettytable
import requests

from pytoys.common import user_input


@dataclasses.dataclass
class Extension(object):
    """Extension object"""
    id: str
    name: str
    version: str
    display_name: str
    publisher_id: str
    publisher_name: str
    publisher_display_name: str
    flags: str = None


class MarketplaceAPI(object):
    BASE_URL = 'https://marketplace.visualstudio.com'

    def __init__(self):
        self.client = requests.Session()

    def get(self, url, params=None):
        """Get a page from the marketplace"""
        resp = self.client.get(parse.urljoin(self.BASE_URL, url.lstrip('/')),
                               params=params)
        resp.raise_for_status()
        return resp

    def post(self, url, json=None):
        """Get a page from the marketplace"""
        resp = self.client.post(parse.urljoin(self.BASE_URL, url.lstrip('/')),
                                json=json)
        resp.raise_for_status()
        return resp

    def search(self, name):
        """Search for plugins in the marketplace"""
        data = {
            "filters": [
                {
                    "criteria": [
                        {
                            "filterType": 8,
                            "value": "Microsoft.VisualStudio.Code"
                        },
                        {
                            "filterType": 10,
                            "value": name
                        },
                    ],
                    "pageNumber": 1,
                    "pageSize": 50,
                    "sortBy": 0,
                    "sortOrder": 0
                }
            ],
        }
        resp = self.post('/_apis/public/gallery/extensionquery', json=data)
        results = json.loads(resp.content).get('results')
        if len(results) < 1:
            return []

        def get_version(extension):
            for version in extension.get('versions') or []:
                if 'version' in version:
                    return version.get('version')

        extensions = results[0].get('extensions', [])
        return [
            Extension(
                id=ext.get('extensionId'),
                name=ext.get('extensionName'),
                version=get_version(ext),
                display_name=ext.get('displayName'),
                publisher_display_name=ext.get('publisher',
                                               {}).get('displayName'),
                publisher_id=ext.get('publisher', {}).get('publisherId'),
                publisher_name=ext.get('publisher', {}).get('publisherName'),
                flags=ext.get('flags', None),
            ) for ext in extensions
        ]

    def download(self, extension: Extension):
        """Download extension from marketplace"""
        logger.info('download extension: {}({})', extension.display_name,
                    extension.name)
        url = f'/_apis/public/gallery/publishers/{extension.publisher_name}/' \
              f'vsextensions/{extension.name}/{extension.version}/vspackage'
        resp = self.get(url)
        matched = re.match(r'.*filename=(.+);', resp.headers.get('content-disposition'))
        filename = matched.group(1) if matched else \
            f'{extension.publisher_name}.{extension.name}-{extension.version}.vsix'

        logger.info('save extension: {}, size: {}', extension.name, resp.headers.get('content-length'))
        with open(filename, 'wb') as f:
            f.write(resp.content)
        logger.success('saved to {}', filename)


def download_extension(name):
    """Download extension from vscode marketplace"""
    marketplace = MarketplaceAPI()
    items = marketplace.search(name)
    if not items:
        raise Exception(f'extension "{name}" not found')

    table = prettytable.PrettyTable(['#', 'extension', 'publisher name',
                                     'version', 'flags'])
    table.align.update({'extension': 'l', 'publisher name': 'l'})
    table.max_width['extension'] = 50
    # table.max_width['flags'] = 20
    for index, item in enumerate(items):
        table.add_row([index+1, item.display_name, item.publisher_display_name,
                       item.version, item.flags])

    print('查询结果:')
    print(table)

    select_index = user_input.get_input_number('请输入要下载的插件序号', min_number=1,
                                              max_number=len(items))
    if select_index is None:
        return
    select_item = items[select_index-1]
    marketplace.download(select_item)
