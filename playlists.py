import argparse
import json
import logging
import os
from typing import List, Dict

from decorators import timer
from utils import save_image_from_url, do_request_validate_response


@timer
def get_tracks_from_playlist(url: str) -> List[Dict]:
    res: List = []
    while url is not None:
        next_res = do_request_validate_response('GET', url, headers={
            "Authorization": "Bearer " + token
        }).json()
        log.debug(next_res['next'])
        res = res + next_res['items']
        url = next_res['next']
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

    user_id: str = do_request_validate_response('GET', 'https://api.spotify.com/v1/me', headers={
        "Authorization": "Bearer " + token
    }).json()['id']

    res: {} = do_request_validate_response('GET', 'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
                                           params={
                                               'limit': 50,
                                               'offset': 0},
                                           headers={"Authorization": "Bearer " + token
                                                    }).json()
    print('Fetched {} playlists.'.format(str(len(res['items']))))

    os.makedirs(os.path.dirname("img/"), exist_ok=True)
    for playlist_meta in res['items']:
        if playlist_meta['images']:
            save_image_from_url(playlist_meta['images'][0]['url'], playlist_meta['id'])

    with open('playlists-metadata.json', 'w+') as f:
        json.dump(res['items'], f, indent=4)

    print('Succesfully wrote {} playlists metadata in playlists-metadata.json'.format(str(len(res['items']))))

    with open('playlist.json', 'w') as f:
        json.dump({
            (playlist['id'] + '#' + playlist['snapshot_id']): get_tracks_from_playlist(
                'https://api.spotify.com/v1/playlists/{}/tracks?fields=next,items(track(name,uri,album(name),artists(name),artist(name)))'
                    .format(playlist['id']))
            for playlist in res['items']
        }, f, indent=4)

    print('The playlists backup has completed succesfully.')
    exit(0)
