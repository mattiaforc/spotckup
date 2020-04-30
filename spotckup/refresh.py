import base64
import logging

import requests as r

from spotckup.utils import do_request_validate_response, path_or_create


def refresh_token(client_id: str, client_secret: str, dir_path: str, refresh_token: str, debug: bool, verbose: str):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    log.info("Client id: " + client_id + "\tClient secret: " + client_secret)

    path: str = path_or_create(dir_path)

    token: str = refresh_token
    if token is None:
        with open(f'{path}/refresh_token', 'r') as f:
            token = f.read()

    res: r.Response = do_request_validate_response('POST', 'https://accounts.spotify.com/api/token', verbose=verbose,
                                                   data={
                                                       'grant_type': "refresh_token",
                                                       'refresh_token': token
                                                   }, headers={
            "Authorization": "Basic " + str(
                base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8'))
        })

    res_json: {} = res.json()
    log.info('Access token: ' + res_json['access_token'])
    log.info('Scopes: ' + res_json['scope'])
    log.info('Expires in: ' + str(res_json['expires_in']))

    with open(f"{path}/access_token", "w+") as f:
        f.write(res_json['access_token'])

    print("Token refreshed.")
    exit(0)
