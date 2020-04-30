import base64
import logging
import os
import uuid
import webbrowser

import requests as r
from spotckup.utils import do_request_validate_response, path_or_create


def auth(client_id: str, client_secret: str, dir_path: str, redirect_uri: str, debug: bool, verbose: bool):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    scopes: str = 'playlist-read-collaborative ' \
                  'playlist-modify-public ' \
                  'playlist-read-private ' \
                  'playlist-modify-private ' \
                  'ugc-image-upload ' \
                  'user-library-modify ' \
                  'user-library-read '

    log.info("Client id: " + client_id + "\tClient secret: " + client_secret)
    random_state = uuid.uuid4()
    log.debug("Generated state: " + random_state.__str__())

    res: r.Response = do_request_validate_response('GET', 'https://accounts.spotify.com/authorize', verbose=verbose,
                                                   params={
                                                       'client_id': client_id,
                                                       'response_type': 'code',
                                                       'redirect_uri': redirect_uri,
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

    res: r.Response = do_request_validate_response('POST', 'https://accounts.spotify.com/api/token', verbose=verbose,
                                                   data={
                                                       'grant_type': "authorization_code",
                                                       'code': tokens['code'],
                                                       'redirect_uri': redirect_uri
                                                   }, headers={
            "Authorization": "Basic " + str(
                base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8'))
        })

    res_json: {} = res.json()
    log.info('Access token: ' + res_json['access_token'])
    log.info('Scopes: ' + res_json['scope'])
    log.info('Expires in: ' + str(res_json['expires_in']))
    log.info('Refresh token: ' + res_json['refresh_token'])

    path: str = path_or_create(dir_path)
    with open(f"{path}/access_token", "w+") as f:
        f.write(res_json['access_token'])

    with open(f"{path}/refresh_token", "w+") as f:
        f.write(res_json['refresh_token'])

    print("Done. Tokens saved in files access_token and refresh_token.\n" +
          "You may now want to run the spotckup script or set the cron job for refreshing automatically the token." +
          "Read the README file for more infos.")
    exit(0)
