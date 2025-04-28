from urllib import parse

import requests
from loguru import logger

RESP_TEMPLATE = """Response:
> {method} {url}
> Content-Type: {content_type}

< {status_code} {reason}
< Content-Length: {content_length}
< Body: {content}
"""


class HttpClient:
    """HttpClient with requests"""

    def __init__(self, base_url=None, timeout=None, log_body_limit=128):
        self.base_url = base_url
        self.timeout = timeout
        self.log_body_limit = log_body_limit
        self.session = requests.Session()
        self.session.hooks['response'].append(self.hook_log_response)

    def hook_log_response(self, response: requests.Response, **kwargs):
        """Log response"""
        resp_content_type = response.headers.get('Content-Type')
        response_content = ''
        if resp_content_type:
            if 'application/json' in resp_content_type or \
               'text/html' in resp_content_type:
                response_content = response.content[0:self.log_body_limit]
                if len(response.content) > self.log_body_limit:
                    response_content += b'...'
        if not response_content:
            response_content = f'<type: {resp_content_type}>'

        logger.debug(RESP_TEMPLATE,
                     method=response.request.method, url=response.request.url,
                     content_type=response.request.headers.get('Content-Type'),
                     status_code=response.status_code,
                     reason=response.reason,
                     content_length=response.headers.get('Content-Length', ''),
                     content=response_content)
        return response

    def _request(self, method, url, **kwargs):
        """http request"""
        if url.startswith('https://') or url.startswith('http://'):
            req_url = url
        else:
            req_url = parse.urljoin(self.base_url, url.lstrip('/'))
        logger.debug("Request: {} {}, params={}", method, req_url,
                     kwargs.get('params', ''))
        resp = self.session.request(method, req_url, timeout=self.timeout,
                                    **kwargs)
        resp.raise_for_status()
        return resp

    def get(self, url, params=None):
        """http get"""
        return self._request('GET', url, params=params)

    def post(self, url, json=None):
        """http post"""
        return self._request('POST', url, json=json)
