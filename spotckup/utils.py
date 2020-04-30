import logging

import requests as r

from spotckup.decorators import timer


@timer
def save_image_from_url(url: str, img_name: str) -> None:
    img_res: r.Response = do_request_validate_response('GET', url, stream=True)
    img_res.raw.decode_content = True
    img = img_res.content  # Binary content!
    with open("img/{}.jpg".format(img_name), 'wb') as img_file:
        img_file.write(img)


@timer
def do_request_validate_response(method: str, url: str, verbose: bool = False, **kwargs) -> r.Response:
    log = logging.getLogger('')
    log.debug(f"Requesting: {method} {url}")
    if verbose:
        log.debug(**kwargs)
    res = r.request(method, url, **kwargs)
    log.debug(f'Response status code: {res.status_code}')
    if verbose:
        log.debug(res.content)
    if res.status_code not in range(200, 300):
        if res.status_code == 429:
            raise Exception("Too many calls. Retry after {}".format(res.headers.get('Retry-After')))
        raise Exception(
            "StatusCode: {}\nError: {}".format(res.status_code, res.text))
    return res
