from urllib import parse
import re
import io

from loguru import logger
import requests
import tqdm

TYPE_WWW_FORM = 'application/x-www-form-urlencoded'
TYPE_JSON = 'application/json'
TYPE_TEXT_HTML = 'text/html'

RESP_TEMPLATE = """http request:
{request}

{status_code} {reason}
{resp_headers}
Body: {content}

(Elapsed: {elapsed:.3f}s)
"""

class NopProgress:
    """No progress bar"""

    def __init__(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def close(self):
        pass


def _parse_request_to_curl(request: requests.PreparedRequest) -> str:
    cmd = ['curl', f'-X{request.method}', f"'{request.url}'"]
    for k, v in request.headers.items():
        cmd.append(f"-H '{k}: {v}'")
    req_type = request.headers.get('content-type')
    if req_type in ['application/json', 'text/html'] \
       and isinstance(request.body, bytes):
        cmd.append(f"-d '{request.body.decode()}'")
    elif isinstance(request.body, str):
        cmd.append(f"-d '{request.body}'")
    elif request.body:
        cmd.append(f"-d <type: {req_type}>")
    return ' '.join(cmd)


class HttpClient:
    """HttpClient with requests"""

    def __init__(self, base_url, timeout=None, log_body_limit=128):
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
                'text/html' in resp_content_type or \
                'text/plain' in resp_content_type):
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
                     content=self._get_log_body(resp),
                     elapsed=resp.elapsed.total_seconds())
        return resp

    def _request(self, method, url, **kwargs) -> requests.Response:
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

    def get(self, url, params=None, stream=False,
            headers=None) -> requests.Response:
        """http get"""
        return self._request('GET', url, params=params, stream=stream,
                             headers=headers)

    def post(self, url, data=None, json=None,
             headers=None)  -> requests.Response:
        """http post"""
        return self._request('POST', url, data=data, json=json,
                             headers=headers)

    def download(self, url, params=None, default_filename=None,
                 progress=False):
        """http download"""
        resp = self.get(url, params=params, stream=True)
        matched = re.match(r'.*filename=(.+);',
                           resp.headers.get('content-disposition') or '')
        if matched:
            filename = matched.group(1)
        elif default_filename:
            filename = default_filename
        else:
            filename = url.split('/')[-1]

        logger.info('save to {}, size: {}', filename,
                    resp.headers.get('content-length'))
        total = resp.headers.get("content-length")
        if total and progress:
            progressbar = tqdm.tqdm(desc=f"Downloading {filename}",
                                    total=int(total), unit='iB')
        else:
            progressbar = NopProgress()

        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE):
                f.write(chunk)
                logger.debug(f"write {len(chunk)} bytes")
                progressbar.update(len(chunk))
