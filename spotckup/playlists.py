import json
import logging
import os
from typing import List, Dict

from spotckup.decorators import timer
from spotckup.utils import save_image_from_url, do_request_validate_response


@timer
def get_tracks_from_playlist(url: str) -> List[Dict]:
    res: List = []
    log: logging.Logger = logging.getLogger('')
    while url is not None:
        next_res = do_request_validate_response('GET', url, headers={
            "Authorization": "Bearer " + token
        }).json()
        log.debug(next_res['next'])
        res = res + next_res['items']
        url = next_res['next']
    return res


def backup_playlist(authorization_token, debug, verbose):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    token: str = authorization_token
    if token is None:
        with open('../data/access_token', 'r') as f:
            token = f.read()

    user_id: str = do_request_validate_response('GET', 'https://api.spotify.com/v1/me',
                                                verbose=verbose,
                                                headers={
                                                    "Authorization": "Bearer " + token
                                                }).json()['id']

    res: {} = do_request_validate_response('GET', 'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
                                           verbose=verbose,
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

    with open('../data/playlists-metadata.json', 'w+') as f:
        json.dump(res['items'], f, indent=4)

    print('Succesfully wrote {} playlists metadata in playlists-metadata.json'.format(str(len(res['items']))))

    with open('../data/playlist.json', 'w') as f:
        json.dump({
            (playlist['id'] + '#' + playlist['snapshot_id']): get_tracks_from_playlist(
                'https://api.spotify.com/v1/playlists/{}/tracks?fields=next,items(is_local,track(name,uri,album(name),artists(name),artist(name)))'
                    .format(playlist['id']))
            for playlist in res['items']
        }, f, indent=4)

    print('The playlists backup has completed succesfully.')
