import argparse
import json
import logging

import requests as r

from utils import do_request_validate_response

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

    with open('library.json', 'r') as f:
        library = json.load(f)
        print(f"Read from local backup {len(library)} albums.")

    for i in range(0, len(library), 50):
        chunk = [el['id'] for el in library[i:i + 50]]
        log.debug(chunk)
        res: r.Response = do_request_validate_response('PUT',
                                                       f'https://api.spotify.com/v1/me/albums',
                                                       data=json.dumps({'ids': chunk}),
                                                       headers={
                                                           "Authorization": "Bearer " + token,
                                                           "Content-Type": "application/json"
                                                       })
        del res

    print('The albums were imported in the spotify library succesfully.')
    exit(0)
