import argparse
import base64
import logging

import requests as r
from utils import do_request_validate_response

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')

    parser = argparse.ArgumentParser(prog='spotckup',
                                     description='Create JSON local backup of music and playlists from a user spotify library')
    parser.add_argument('client_id', metavar='<Client ID>', type=str, help='Spotify app client id')
    parser.add_argument('client_secret', metavar='<Client Secret>', type=str, help='Spotify app client secret')
    parser.add_argument('--refresh_token', metavar='<refresh token>', type=str, nargs='?', default=None,
                        help='The refresh token obtained from the /authorize endpoint')
    parser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False,
                        help='Run script in debug mode')
    args = parser.parse_args()
    if args.debug: log.setLevel('DEBUG')

    log.info("Client id: " + args.client_id + "\tClient secret: " + args.client_secret)

    token: str = args.refresh_token
    if token is None:
        with open('refresh_token', 'r') as f:
            token = f.read()

    res: r.Response = do_request_validate_response('POST', 'https://accounts.spotify.com/api/token', data={
        'grant_type': "refresh_token",
        'refresh_token': token
    }, headers={
        "Authorization": "Basic " + str(
            base64.b64encode(bytes(args.client_id + ':' + args.client_secret, 'utf-8')).decode('utf-8'))
    })

    res_json: {} = res.json()
    log.info('Access token: ' + res_json['access_token'])
    log.info('Scopes: ' + res_json['scope'])
    log.info('Expires in: ' + str(res_json['expires_in']))

    with open("./access_token", "w+") as f:
        f.write(res_json['access_token'])

    print("Token refreshed.")
    exit(0)
