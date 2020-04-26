import argparse
import json
import logging
from hashlib import md5
from typing import Dict, List

import requests as r


def get_tracks_from_playlist(url: str):
    res: List = []
    while url is not None:
        next_res = r.get(url, headers={
            "Authorization": "Bearer " + token
        }).json()
        log.debug(next_res['next'])
        res = res + next_res['items']
        url = next_res['next']
    return res


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger(__name__)

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

    user_id = r.get('https://api.spotify.com/v1/me', headers={
        "Authorization": "Bearer " + token
    }).json()['id']

    res: r.Response = r.get('https://api.spotify.com/v1/users/{}/playlists'.format(user_id), params={
        'limit': 50,
        'offset': 0
    }, headers={
        "Authorization": "Bearer " + token
    })

    log.debug('Response status code: ' + str(res.status_code))
    if res.status_code != 200:
        if res.status_code == 429:
            raise Exception("Too many calls. Retry after {}".format(res.headers.get('Retry-After')))
        raise Exception("Could not obtain playlists")

    res_json: {} = res.json()
    print('Fetched {} playlists.'.format(str(len(res_json['items']))))

    with open('playlists-metadata.json', 'w+') as f:
        json.dump(res_json['items'], f)

    print('Succesfully wrote {} playlists metadata in playlists-metadata.json'.format(str(len(res_json['items']))))

    with open('playlist.json', 'w') as f:
        json.dump({
            md5((playlist['id'] + playlist['snapshot_id']).encode('utf-8')).hexdigest(): get_tracks_from_playlist(
                'https://api.spotify.com/v1/playlists/{}/tracks?fields=next,items(track(name,uri,album(name),artists(name),artist(name)))'
                    .format(playlist['id']))
            for playlist in res_json['items']
        }, f, indent=4)

    print('Successful backup of all playlists.')
    exit(0)
