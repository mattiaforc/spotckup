import base64
import json
import logging
import os

import requests as r

from spotckup.utils import do_request_validate_response, path_or_create


def restore_playlist(authorization_token: str, dir_path: str, debug: bool, verbose: bool):
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger('')
    if debug: log.setLevel('DEBUG')

    path: str = path_or_create(dir_path)

    token: str = authorization_token
    if token is None:
        with open(f'{path}/access_token', 'r') as f:
            token = f.read()

    user_id: str = do_request_validate_response('GET', 'https://api.spotify.com/v1/me', verbose=verbose, headers={
        "Authorization": "Bearer " + token
    }).json()['id']

    with open(f'{path}/playlists-metadata.json', 'r') as f:
        playlists_metadata = json.load(f)
        print(f"Read from local backup {len(playlists_metadata)} playlists.")

    link_metadata: {} = {}
    imgs_urls: {} = {}

    for playlist_meta in playlists_metadata:
        if len(playlist_meta) == 0: break
        res: r.Response = do_request_validate_response('POST',
                                                       'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
                                                       verbose=verbose,
                                                       data=json.dumps({
                                                           'name': playlist_meta['name'],
                                                           'public': str(playlist_meta['public']),
                                                           'collaborative': str(playlist_meta['collaborative']),
                                                           'description': playlist_meta['description']
                                                       }),
                                                       headers={
                                                           "Authorization": "Bearer " + token,
                                                           "Content-type": "application/json"
                                                       })
        res_json = res.json()
        link_metadata[playlist_meta['id']] = res_json['id']
        if len(playlist_meta['images']) != 0:
            log.debug('Playlist cover: ' + playlist_meta['images'][0]['url'])
            imgs_urls[playlist_meta['id']] = playlist_meta['images'][0]['url']
        log.debug(f'Succesfuly created playlist {playlist_meta["name"]}.\nStatus code: {res.status_code}')
        log.debug(f"New id: {res.json()['id']}")
        del res

    with open(f'{path}/playlist.json', 'r') as f:
        playlists = json.load(f)
        for playlist in playlists:
            old_id = playlist.split('#')[0]
            id = link_metadata[old_id]
            img = None

            if os.path.exists(f'{path}/img/{old_id}.jpg') and os.path.isfile(f'{path}/img/{old_id}.jpg'):
                with open(f'{path}/img/{old_id}.jpg', 'rb') as img_file:
                    img = img_file.read()
            elif old_id in imgs_urls:
                img_res: r.Response = do_request_validate_response('GET', imgs_urls[old_id],
                                                                   verbose=verbose, stream=True)
                img_res.raw.decode_content = True
                img = img_res.content  # Binary content!
                with open(f'{path}/img/{old_id}.jpg', 'wb') as img_file:
                    img_file.write(img)
            playlist_no_local = list(filter(lambda track: not track['is_local'], playlists[playlist]))
            for i in range(0, len(playlist_no_local), 100):
                chunk = [track['track']['uri'] for track in playlist_no_local[i:i + 100]]
                do_request_validate_response('POST',
                                             f'https://api.spotify.com/v1/playlists/{id}/tracks',
                                             verbose=verbose,
                                             data=json.dumps({
                                                 "uris": chunk
                                             }),
                                             headers={
                                                 "Authorization": "Bearer " + token,
                                                 "Content-Type": "application/json"
                                             })

            if img is not None:
                do_request_validate_response('PUT',
                                             f'https://api.spotify.com/v1/playlists/{id}/images',
                                             verbose=verbose,
                                             data=base64.b64encode(img).decode('utf-8'),
                                             headers={
                                                 "Authorization": "Bearer " + token,
                                                 "Content-Type": "image/jpeg"
                                             })

    print('The playlists were imported on spotify succesfully.')
