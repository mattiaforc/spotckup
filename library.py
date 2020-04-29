import argparse
import json
import logging
from typing import List

from utils import do_request_validate_response


def get_tracks_from_albums(url: str):
    res: List = []
    while url is not None:
        next_res = do_request_validate_response('GET', url, headers={
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
        log.debug(url)
    return res


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')

    parser = argparse.ArgumentParser(prog='spotckup',
                                     description='Create JSON local backup of music and playlists from a user spotify library')
    parser.add_argument('--authorization_token', metavar='<authorization token>', type=str, nargs='?', default=None,
                        help='The authorization token obtained from the /authorize endpoint')
    parser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False,
                        help='Run script in debug mode')
    args = parser.parse_args()
    if args.debug: log.setLevel('DEBUG')

    token: str = args.authorization_token
    if token is None:
        with open('access_token', 'r') as f:
            token = f.read()

    print("Fetching albums from library...")
    with open('library.json', 'w') as f:
        json.dump(get_tracks_from_albums('https://api.spotify.com/v1/me/albums?limit=50')
                  , f, indent=4)

    print('Successful backup of all library.')
    exit(0)
