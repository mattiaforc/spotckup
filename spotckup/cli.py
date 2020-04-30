import click
import os
import shutil

from spotckup import authorize, refresh as ref, library, playlists, restore_playlists, restore_library

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0')
def spotckup():
    pass


@spotckup.command()
def clear():
    if str(input(
            "Attention! You are going to delete all local files, including access/refresh tokens, cover images and "
            "playlists/library from default directory ~/Documents/spotckup.\n\n"
            "Are you sure? (y/[n]):\t")) == 'y':
        shutil.rmtree(os.path.join(os.path.expanduser('~'), 'Documents/spotckup'), ignore_errors=True)


@spotckup.command()
@click.option('--client-id', default=os.getenv('SPOTIFY_CLIENT_ID'))
@click.option('--client-secret', default=os.getenv('SPOTIFY_CLIENT_SECRET'))
@click.option('--redirect-uri', default='http://localhost', help='The redirect uri defined in the spotify web app.'
                                                                 + ' If the provided uri does not match the spotify one '
                                                                 + 'the authorization will fail.')
@click.option('-p', '--path', default='',
              help='The path to the directory where you want to store tokens and backup data')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug log more verbose.')
def auth(client_id, client_secret, path, redirect_uri, debug, verbose):
    validate_id_and_secret(client_id, client_secret)
    authorize.auth(client_id, client_secret, path, redirect_uri, debug, verbose)


@spotckup.command()
@click.option('--token', '-t', default=None,
              help='The access token, if this option is not present it will try to read it '
                   + 'from data/access_token')
@click.option('-p', '--path', default='',
              help='The path to the directory where you want to store tokens and backup data')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug logs more verbose.')
@click.option('--only-library', default=False, is_flag=True, help='Set this flag to backup only the library')
@click.option('--only-playlist', default=False, is_flag=True, help='Set this flag to backup only the playlists')
def backup(token, path, debug, verbose, only_library, only_playlist):
    if not only_playlist: library.backup_library(token, path, debug, verbose)
    if not only_library: playlists.backup_playlist(token, path, debug, verbose)
    exit(0)


@spotckup.command()
@click.option('--token', '-t', default=None,
              help='The access token, if this option is not present it will try to read it '
                   + 'from data/access_token')
@click.option('-p', '--path', default='',
              help='The path to the directory where you want to store tokens and backup data')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug logs more verbose.')
@click.option('--only-library', default=False, is_flag=True, help='Set this flag to restore only the library')
@click.option('--only-playlist', default=False, is_flag=True, help='Set this flag to restore only the playlists')
def restore(token, path, debug, verbose, only_library, only_playlist):
    if not only_playlist: restore_library.restore_library(token, path, debug, verbose)
    if not only_library: restore_playlists.restore_playlist(token, path, debug, verbose)
    exit(0)


@spotckup.command()
@click.option('--client-id', default=os.getenv('SPOTIFY_CLIENT_ID'))
@click.option('--client-secret', default=os.getenv('SPOTIFY_CLIENT_SECRET'))
@click.option('--token', '-t', default=None,
              help='The refresh token, if this option is not present it will try to read it '
                   + 'from data/refresh_token')
@click.option('-p', '--path', default='',
              help='The path to the directory where you want to store tokens and backup data')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug log more verbose.')
def refresh(client_id, client_secret, token, path, debug, verbose):
    validate_id_and_secret(client_id, client_secret)
    ref.refresh_token(client_id, client_secret, path, token, debug, verbose)


def validate_id_and_secret(client_id: str, client_secret: str):
    if client_id is None or client_id is '':
        print("Client ID is mandatory. You can either set an environment variable named SPOTIFY_CLIENT_ID "
              + "or pass it with the --client-id flag.")
        exit(1)
    if client_secret is None or client_secret is '':
        print("Client secret is mandatory. You can either set an environment variable named SPOTIFY_CLIENT_SECRET "
              + "or pass it with the --client-secret flag.")
        exit(1)


if __name__ == '__main__':
    spotckup()
