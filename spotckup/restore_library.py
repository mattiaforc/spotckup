import argparse
import json
import logging

import requests as r

from spotckup.utils import do_request_validate_response


def restore_library(authorization_token: str, debug: bool, verbose: bool):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    token: str = authorization_token
    if token is None:
        with open('../data/access_token', 'r') as f:
            token = f.read()

    with open('../data/library.json', 'r') as f:
        library = json.load(f)
        print(f"Read from local backup {len(library)} albums.")

    for i in range(0, len(library), 50):
        chunk = [el['id'] for el in library[i:i + 50]]
        log.debug(chunk)
        res: r.Response = do_request_validate_response('PUT',
                                                       f'https://api.spotify.com/v1/me/albums',
                                                       verbose=verbose,
                                                       data=json.dumps({'ids': chunk}),
                                                       headers={
                                                           "Authorization": "Bearer " + token,
                                                           "Content-Type": "application/json"
                                                       })
        del res

    print('The albums were imported in the spotify library succesfully.')
