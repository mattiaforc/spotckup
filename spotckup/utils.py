import logging
import os

import requests as r
from spotckup.decorators import timer


@timer
def save_image_from_url(url: str, img_name: str, path: str) -> None:
    img_res: r.Response = do_request_validate_response('GET', url, stream=True)
    img_res.raw.decode_content = True
    img = img_res.content  # Binary content!
    with open("{}/{}.jpg".format(path, img_name), 'wb') as img_file:
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


def path_or_create(dir_path: str) -> str:
    path = os.path.join(os.path.expanduser('~'), 'Documents/spotckup/data')
    if dir_path is not '' and dir_path is not None:
        path = dir_path
    logging.getLogger('').info(path)

    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"The specified path '{path}' is not a directory")
    else:
        create_flag: bool = True if str(
            input(f"The specified path '{path}' does not exist. Do you want to create it? (y/[n])")) == 'y' else False
        if create_flag:
            os.makedirs(path, exist_ok=True)
        else:
            print("Did not create the directory. Exiting application...")
            exit(1)
    return path
