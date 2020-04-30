import json
import logging
from typing import List

from spotckup.utils import do_request_validate_response


def get_tracks_from_albums(url: str, token: str, verbose: bool = False):
    res: List = []
    while url is not None:
        next_res = do_request_validate_response('GET', url, verbose=verbose, headers={
            "Authorization": "Bearer " + token
        }).json()
        res = res + [
            {
                'id': album['album']['id'],
                'name': album['album']['name'],
                'artists': list(map(lambda a: a['name'], album['album']['artists']))
            }
            for album in next_res['items']
        ]
        url = next_res['next']
        log: logging.Logger = logging.getLogger('')
        log.debug(url)
    return res


def backup_library(authorization_token, debug, verbose):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    token: str = authorization_token
    if token is None:
        with open('../data/access_token', 'r') as f:
            token = f.read()

    print("Fetching albums from library...")
    with open('../data/library.json', 'w') as f:
        json.dump(get_tracks_from_albums('https://api.spotify.com/v1/me/albums?limit=50', token, verbose=verbose)
                  , f, indent=4)

    print('Successful backup of all library.')
