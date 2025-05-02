"""VSCode extension api from marketplace"""
import dataclasses
import json
import re

from loguru import logger

from pytoys.common import user_input
from pytoys.common import httpclient


@dataclasses.dataclass
class Extension:
    """Extension object"""
    id: str
    name: str
    version: str
    display_name: str
    publisher_id: str
    publisher_name: str
    publisher_display_name: str
    flags: str = None


class ExtensionNotFound(Exception):
    """Extension not found exception"""

    def __init__(self, name):
        super().__init__(f'extension "{name}" not found')


class MarketplaceAPI(httpclient.HttpClient):
    """Marketplace API"""

    def __init__(self):
        super().__init__('https://marketplace.visualstudio.com')

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
        logger.info('search extension: {}', name)
        resp = self.post('/_apis/public/gallery/extensionquery', json=data)
        results = json.loads(resp.content).get('results')
        if len(results) < 1:
            return []

        def get_version(extension):
            for version in extension.get('versions') or []:
                if 'version' in version:
                    return version.get('version')
            return None

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

    def download(self, ext: Extension):
        """Download extension from marketplace"""
        logger.info('download extension: {}({})', ext.display_name,
                    ext.name)
        url = f'/_apis/public/gallery/publishers/{ext.publisher_name}/' \
              f'vsextensions/{ext.name}/{ext.version}/vspackage'
        resp = self.get(url)
        matched = re.match(r'.*filename=(.+);',
                           resp.headers.get('content-disposition'))
        filename = matched.group(1) if matched else \
            f'{ext.publisher_name}.{ext.name}-{ext.version}.vsix'

        logger.info('save extension: {}, size: {}', ext.name,
                    resp.headers.get('content-length'))
        with open(filename, 'wb') as f:
            f.write(resp.content)
        logger.success('saved to {}', filename)


def download_extension(name):
    """Download extension from vscode marketplace"""
    marketplace = MarketplaceAPI()
    items = marketplace.search(name)
    if not items:
        raise ExtensionNotFound(name)

    item = user_input.select_items(
        [dataclasses.asdict(item) for item in items],
        {'display_name', 'publisher_display_name', 'version', 'flags'},
        title={'display_name': '插件', 'publisher_display_name': '发布者',
               'version': '版本', 'flags': '标签'},
        select_msg='查询结果:',
    )
    if not item:
        return
    marketplace.download(Extension(**item))
