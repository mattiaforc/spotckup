import argparse
import base64
import json
import logging
import os
import shutil

import requests as r

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    log: logging.Logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(prog='spotckup',
                                     description='Create JSON local backup of music and playlists from a user spotify library')
    parser.add_argument('--authorization_token', metavar='<authorization token>', type=str, nargs='?', default=None,
                        help='The authorization token obtained from the /authorize endpoint')
    parser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False,
                        help='Run script in debug mode')
    parser.add_argument('--no-image-cache', dest='local_img', action='store_const', const=False, default=True,
                        help="If this flag is present, the album/playlists cover images won't be downloaded and stored locally")
    args = parser.parse_args()
    if args.debug: log.setLevel('DEBUG')

    token: str = args.authorization_token
    if token is None:
        with open('access_token', 'r') as f:
            token = f.read()

    user_id = r.get('https://api.spotify.com/v1/me', headers={
        "Authorization": "Bearer " + token
    }).json()['id']

    with open('playlists-metadata.json', 'r') as f:
        playlists_metadata = json.load(f)
        print(f"Read from local backup {len(playlists_metadata)} playlists.")

    link_metadata: {} = {}
    imgs_urls: {} = {}
    os.makedirs(os.path.dirname("img/"), exist_ok=True)

    for playlist_meta in playlists_metadata:
        res: r.Response = r.post('https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
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
        if res.status_code not in [200, 201, 204]:
            raise Exception(
                f"Could not create playlist {playlist_meta['name']} with id: {playlist_meta['id']}.\nError: {res.text}")
        res_json = res.json()
        link_metadata[playlist_meta['id']] = res_json['id']
        if playlist_meta['images'] is not None:
            log.debug('Playlist cover: ' + playlist_meta['images'][0]['url'])
            imgs_urls[playlist_meta['id']] = playlist_meta['images'][0]['url']
        log.debug(f'Succesfuly created playlist {playlist_meta["name"]}.\nStatus code: {res.status_code}')
        log.debug(f"New id: {res.json()['id']}")
        del res

    with open('playlist.json', 'r') as f:
        playlists = json.load(f)
        for playlist in playlists:
            old_id = playlist.split('#')[0]
            id = link_metadata[old_id]
            img = None

            if os.path.exists("img/{}.jpg".format(old_id)) and os.path.isfile("img/{}.jpg".format(old_id)):
                with open("img/{}.jpg".format(old_id), 'rb') as img_file:
                    img = img_file.read()
            elif old_id in imgs_urls:
                img_res = r.get(imgs_urls[old_id], stream=True)
                img_res.raw.decode_content = True
                img = img_res.content  # Binary content!
                with open("img/{}.jpg".format(old_id), 'wb') as img_file:
                    img_file.write(img)
            for i in range(0, len(playlists[playlist]), 100):
                chunk = [track['track']['uri'] for track in playlists[playlist][i:i + 100]]
                res = r.post(f'https://api.spotify.com/v1/playlists/{id}/tracks', data=json.dumps({
                    "uris": chunk
                }), headers={
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json"
                })
                log.debug(f'Status code: {res.status_code}')
                if res.status_code not in [200, 201, 204]:
                    raise Exception(f"Error in adding tracks. Error: {res.text}")
                log.debug(f'Added chunk of {len(chunk)} tracks in playlist {id}')

            if img is not None:
                res = r.put(f'https://api.spotify.com/v1/playlists/{id}/images',
                            data=base64.b64encode(img).decode('utf-8'),
                            headers={
                                "Authorization": "Bearer " + token,
                                "Content-Type": "image/jpeg"
                            })
            log.debug('Response code: ' + str(res.status_code))
            if res.status_code not in [200, 201, 202, 204]:
                raise Exception(
                    f"Error when uploading cover image for playlist {id}.\nError: {res.content}")
            del res

    print('The playlists were imported on spotify succesfully.')
    exit(0)
