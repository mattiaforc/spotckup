import json
import logging
import os
from typing import List, Dict

from spotckup.decorators import timer
from spotckup.utils import save_image_from_url, do_request_validate_response, path_or_create


@timer
def get_list_from_paginated_response(url: str, token: str, verbose: bool = False) -> List[Dict]:
    res: List = []
    log: logging.Logger = logging.getLogger('')
    while url is not None:
        next_res = do_request_validate_response('GET', url, verbose=verbose, headers={
            "Authorization": "Bearer " + token
        }).json()
        log.debug(next_res['next'])
        res = res + next_res['items']
        url = next_res['next']
    return res


def backup_playlist(authorization_token, dir_path, debug, verbose):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    path: str = path_or_create(dir_path)

    token: str = authorization_token
    if token is None:
        with open(f'{path}/access_token', 'r') as f:
            token = f.read()

    user_id: str = do_request_validate_response('GET', 'https://api.spotify.com/v1/me',
                                                verbose=verbose,
                                                headers={
                                                    "Authorization": "Bearer " + token
                                                }).json()['id']

    playlists: [] = get_list_from_paginated_response(f'https://api.spotify.com/v1/users/{user_id}/playlists', token,
                                                     verbose=verbose)
    # playlists: {} = do_request_validate_playlistsponse('GET', 'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
    #                                        verbose=verbose,
    #                                        params={
    #                                            'limit': 50,
    #                                            'offset': 0},
    #                                        headers={"Authorization": "Bearer " + token
    #                                                 }).json()
    print('Fetched {} playlists.'.format(str(len(playlists))))

    os.makedirs(os.path.dirname(f"{path}/img/"), exist_ok=True)
    for playlist_meta in playlists:
        if playlist_meta['images']:
            if not os.path.exists(f'{path}/img/{playlist_meta["id"]}.jpg'):
                save_image_from_url(playlist_meta['images'][0]['url'], playlist_meta['id'], f'{path}/img')

    with open(f'{path}/playlists-metadata.json', 'w+') as f:
        json.dump(playlists, f, indent=4)

    log.info('Succesfully wrote {} playlists metadata in playlists-metadata.json'.format(str(len(playlists))))

    with open(f'{path}/playlist.json', 'w') as f:
        json.dump({
            (playlist['id'] + '#' + playlist['snapshot_id']): get_list_from_paginated_response(
                'https://api.spotify.com/v1/playlists/{}/tracks?fields=next,items(is_local,track(name,uri,album(name),artists(name),artist(name)))'
                    .format(playlist['id']), token, verbose=verbose)
            for playlist in playlists
        }, f, indent=4)

    print('The playlists backup has completed succesfully.')
