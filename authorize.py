import argparse
import base64
import logging
import uuid
import webbrowser

import requests as r
from utils import do_request_validate_response

# nzksazdwlqtmfkmikw@awdrt.org
# Password1234-

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')

    parser = argparse.ArgumentParser(prog='spotckup',
                                     description='Create JSON local backup of music and playlists from a user spotify library')
    parser.add_argument('client_id', metavar='<Client ID>', type=str, help='Spotify app client id')
    parser.add_argument('client_secret', metavar='<Client Secret>', type=str, help='Spotify app client secret')
    parser.add_argument('--redirect_uri', metavar='<Redirect URI>', type=str, nargs='?', default='http://localhost',
                        help='The redirect uri as configured in the spotify developer dashboard app')
    parser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False,
                        help='Run script in debug mode')
    args = parser.parse_args()
    if args.debug: log.setLevel('DEBUG')

    scopes: str = 'playlist-read-collaborative ' \
                  'playlist-modify-public ' \
                  'playlist-read-private ' \
                  'playlist-modify-private ' \
                  'ugc-image-upload ' \
                  'user-library-modify ' \
                  'user-library-read '

    log.info("Client id: " + args.client_id + "\tClient secret: " + args.client_secret)
    random_state = uuid.uuid4()
    log.debug("Generated state: " + random_state.__str__())

    res: r.Response = do_request_validate_response('GET', 'https://accounts.spotify.com/authorize', params={
        'client_id': args.client_id,
        'response_type': 'code',
        'redirect_uri': args.redirect_uri,
        'state': random_state,
        'scope': scopes
    })

    print('Opening browser... Log in spotify and paste here the url the browser redirects you to.')
    webbrowser.open(res.url, new=2)
    res_url = str(input("Url: - something like redirect_uri?code=AQB-w...&state=3ae...\n"))
    tokens = {k: v for k, v in [qp.split("=", 2) for qp in res_url.split("?", 1)[1].split("&")]}

    if 'error' in tokens: raise Exception("The browser did not authorize the request")

    log.debug('Received state: ' + tokens['state'])
    log.info('Authorization code: ' + tokens['code'])
    if tokens['state'] != random_state.__str__(): raise Exception("Invalid state")

    res: r.Response = do_request_validate_response('POST', 'https://accounts.spotify.com/api/token', data={
        'grant_type': "authorization_code",
        'code': tokens['code'],
        'redirect_uri': args.redirect_uri
    }, headers={
        "Authorization": "Basic " + str(
            base64.b64encode(bytes(args.client_id + ':' + args.client_secret, 'utf-8')).decode('utf-8'))
    })

    res_json: {} = res.json()
    log.info('Access token: ' + res_json['access_token'])
    log.info('Scopes: ' + res_json['scope'])
    log.info('Expires in: ' + str(res_json['expires_in']))
    log.info('Refresh token: ' + res_json['refresh_token'])

    with open("./access_token", "w+") as f:
        f.write(res_json['access_token'])

    with open("./refresh_token", "w+") as f:
        f.write(res_json['refresh_token'])

    print("Done. Tokens saved in files access_token and refresh_token.\n" +
          "You may now want to run the spotckup script or set the cron job for refreshing automatically the token." +
          "Read the README file for more infos.")
    exit(0)
