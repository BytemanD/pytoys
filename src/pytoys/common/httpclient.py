from urllib import parse

import requests
from loguru import logger

RESP_TEMPLATE = """http request:
{request}

{status_code} {reason}
{resp_headers}
Body: {content}
"""

def _parse_request_to_curl(request: requests.Request) -> str:
    cmd = ['curl', f'-X{request.method}', f"'{request.url}'"]
    for k, v in request.headers.items():
        cmd.append(f"-H '{k}: {v}'")
    req_type = request.headers.get('content-type')
    if req_type in ['application/json', 'text/html']:
        cmd.append(f"-d '{request.body.decode()}'")
    elif request.body:
        cmd.append(f"<type: {req_type}>")
    return ' '.join(cmd)


class HttpClient:
    """HttpClient with requests"""

    def __init__(self, base_url=None, timeout=None, log_body_limit=128):
        self.base_url = base_url
        self.timeout = timeout
        self.log_body_limit = log_body_limit
        self.session = requests.Session()
        self.session.hooks['response'].append(self._hook_log_response)

    def _get_log_body(self, resp: requests.Response):
        resp_content_type = resp.headers.get('Content-Type')
        resp_content = ''
        if resp_content_type \
           and ('application/json' in resp_content_type or \
                'text/html' in resp_content_type):
            resp_content = resp.content.decode()
        if len(resp_content) > self.log_body_limit:
            resp_content = resp_content[0:self.log_body_limit] +'...'

        if not resp_content:
            resp_content = f'<type: {resp_content_type}>'
        elif len(resp_content) > self.log_body_limit:
            resp_content = resp_content[0:self.log_body_limit] +'...'
        return resp_content

    def _hook_log_response(self, resp: requests.Response, **kwargs): # pylint: disable=unused-argument
        """Log response"""

        def _parse_resp_headers(headers):
            return '\n'.join([f'{k}: {v}' for k, v in headers.items()])

        logger.debug(RESP_TEMPLATE,
                     request=_parse_request_to_curl(resp.request),
                     status_code=resp.status_code, reason=resp.reason,
                     resp_headers=_parse_resp_headers(resp.headers),
                     content=self._get_log_body(resp))
        return resp

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
