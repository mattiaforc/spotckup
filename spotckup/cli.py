import click

from spotckup import authorize, refresh as ref, library, playlists, restore_playlists, restore_library

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0')
def spotckup():
    pass


@spotckup.command()
@click.argument('client-id')
@click.argument('client-secret')
@click.option('--redirect-uri', default='http://localhost', help='The redirect uri defined in the spotify web app.'
                                                                 + ' If the provided uri does not match the spotify one '
                                                                 + 'the authorization will fail.')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug log more verbose.')
def auth(client_id, client_secret, redirect_uri, debug, verbose):
    authorize.auth(client_id, client_secret, redirect_uri, debug, verbose)


@spotckup.command()
@click.option('--token', '-t', default=None,
              help='The access token, if this option is not present it will try to read it '
                   + 'from data/access_token')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug logs more verbose.')
@click.option('--only-library', default=False, is_flag=True, help='Set this flag to backup only the library')
@click.option('--only-playlist', default=False, is_flag=True, help='Set this flag to backup only the playlists')
def backup(token, debug, verbose, only_library, only_playlist):
    if not only_playlist: library.backup_library(token, debug, verbose)
    if not only_library: playlists.backup_playlist(token, debug, verbose)
    exit(0)


@spotckup.command()
@click.option('--token', '-t', default=None,
              help='The access token, if this option is not present it will try to read it '
                   + 'from data/access_token')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug logs more verbose.')
@click.option('--only-library', default=False, is_flag=True, help='Set this flag to restore only the library')
@click.option('--only-playlist', default=False, is_flag=True, help='Set this flag to restore only the playlists')
def restore(token, debug, verbose, only_library, only_playlist):
    if not only_playlist: restore_library.restore_library(token, debug, verbose)
    if not only_library: restore_playlists.restore_playlist(token, debug, verbose)
    exit(0)


@spotckup.command()
@click.argument('client-id')
@click.argument('client-secret')
@click.option('--token', '-t', default=None,
              help='The refresh token, if this option is not present it will try to read it '
                   + 'from data/refresh_token')
@click.option('--debug', '-d', default=False, is_flag=True, help='Enable debug output.')
@click.option('--verbose', default=False, is_flag=True, help='Makes debug log more verbose.')
def refresh(client_id, client_secret, token, debug, verbose):
    ref.refresh_token(client_id, client_secret, token, debug, verbose)


if __name__ == '__main__':
    spotckup()
