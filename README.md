# Spotckup
![](https://img.shields.io/pypi/v/spotckup?color=blue) ![](https://img.shields.io/pypi/l/spotckup)

Spotckup is a small utility for easy local json backup of spotify library and playlists.
You can install it with `pip` by using the command
```sh
pip install spotckup
``` 
or if you want you can clone the repository, build it manually with `setuptools` by running the script `build.sh` and
then install it (assuming you are in the root directory) with
```sh
pip install dist/spotckup_mattiaforc-0.1.0-py3-none-any.whl
```  
## Usage
**Available commands** (use `spotckup <command> -h` or `spotckup <command> --help` for in-depth details):
-   [`spotckup auth`](#authentication-and-refreshing-token) - authorize the app to read/modify spotify library and playlists
-   [`spotckup refresh`](#authentication-and-refreshing-token) - refresh the authentication token obtained with `spotckup auth` (which expires after an hour)
-   [`spotckup backup`](#backup-and-restore) - download and store locally all the playlists and the spotify user library
-   [`spotckup restore`](#backup-and-restore) - export local library and playlists into spotify
-   `spotckup clear` - delete default directory with all backup/token files, i.e. `~/Documents/spotckup`

### Authentication and refreshing token
Before doing any other operation, you have to authorize spotckup to grant him access to the user library/playlist. Run in a terminal the command (the `--client-id` and the `--client-secret` flag in all commands can be omitted by [setting their values as environment variables](#config-environment-variables-optional), which is strongly suggested)
```sh
spotckup auth --client-id <YOUR CLIENT ID> --client-secret <YOUR CLIENT SECRET>
```
and, after loggin in the browser with your spotify account and authorizing the app, copy/paste the redirect url and go back to the terminal that should have already prompted you to insert it.
The redirected url is by default `http://localhost` and I suggest to leave it like this and add it to the web app in the spotify dashboard, unless you have other specific needs. In that case, you can run the `spotckup auth` command with the flag `--redirect_uri <YOUR_URL>` set to whatever url you need.

The token expires in an hour, so before doing any other operation (like backup or restore) you should probably refresh it by running
```sh
spotckup refresh --client-id <YOUR CLIENT ID> --client-secret <YOUR CLIENT SECRET>
```
or you will see a `STATUS CODE 401 - THE ACCESS CODE EXPIRED` response in your log/exception. If you ever want to ignore the stored access/refresh token and use a custom one you can provide it directly to spotckup with the flag `--token` or `-t`, e.g.
```sh
spotckup refresh -t <TOKEN>
```

### Backup and restore
For backing up all your data (library AND playlists), you can use the command 
```sh
spotckup backup 
```
which will automatically fetch the access token in the default directory or in the `-p`, `--path` specified value. If you want to do the local backup of playlists only, you can do so with the flag `--only-playlist`; vice versa to backup only the library you can use `--only-library`:
```sh
spotckup backup --only-playlist
spotckup backup --only-library
```

Restoring and exporting back data to spotify is as simple as doing the backup; use the command
```sh
spotckup restore
```
which allows the exact same flags, i.e. `--only-playlist` and `--only-library`.

Data, such as the playlist/library backup and the authorization/refresh tokens are stored by default in `~/Documents/spotckup/data` and playlist cover images in `~/Documents/spotckup/data/img`. If you want to change this behaviour, you can run every script with the flag `-p` or `--path` and specify your own, like 
```sh
spotckup refresh --path '/path/to/your/directory'
spotckup backup --path '/path/to/your/directory'
```
There is no need to manually create the folders, since spotckup will take care of that, just be sure to have adeguate permissions for writing in the submitted directory. Images will always be stored in the path you specified + `/img`.

The backup, but mostly the restore command can take a long time to be completed, so no need to worry if the terminal seems stuck.
For any other problem, see [debug](#debug)

#### Local tracks
If local tracks are present in any downloaded playlist, they will be stored in the json too; due to the impossibility of actually locating them on the filesystem (spotify does not save those informations) the tracks are only referenced in the json but will **not** be restored when exporting the playlist back to spotify.
To overcome this situation, in a future version (with enough filesystem read permission) a local scan of user-defined "Music" directory could be done, hence finding the local tracks and re-exporting them to spotify playlists. 


### Debug 
For debug purposes, you can run every command with `-d` or `--debug`, which will log debug informations on things like written data, fetched data, http responses and etc. If this is not enough, you may want to combine it with the flag `--verbose` that will make the app log almost every request/response detail.
```sh
spotckup backup --debug --verbose
```

### Config environment variables (Optional)
It is strongly suggested to export the two spotify web app variables (client-id and client-secret, *which can be found in your [developer dashboard](developer.spotify.com/dashboard/) in spotify*) as environment variables.
If you want to do that, you can add the following lines to file `~/.bashrc` or `~/.bash_profile` or`~/.profile`
```sh
export SPOTIFY_CLIENT_ID='<VALUE>'
export SPOTIFY_CLIENT_SECRET='<VALUE>'
```
After saving the file, you could source it via `source ~/.bashrc` or `source ~/.bash_profile` or `source ~/.profile` according to the one you chose in the step before, or logout/login from your os to make changes effective. To check if everything went ok, you should see your inserted values when typing
```sh
echo $SPOTIFY_CLIENT_ID
echo $SPOTIFY_CLIENT_SECRET
```
in a terminal.

### Extra - `cron` job for automatic backups

You may want to backup things on a regular basis by using `cron`.
`cron` is a time-based job scheduler in Unix-like computer operating systems which allows flexible and powerful job scheduling.

First of all, if you don't have `cron` installed, run
```sh
$ sudo apt-get update
$ sudo apt-get install cron 
``` 

and then
```sh
crontab -e
```

which, if run properly, should display a text editor of your choice.
Scroll down to the bottom of the opened crontab file where you can define command lines to be run.
Syntax is:
```
.---------------- minute (0 - 59) 
|  .------------- hour (0 - 23)
|  |  .---------- day of month (1 - 31)
|  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ... 
|  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7)  OR sun,mon,tue,wed,thu,fri,sat 
|  |  |  |  |
*  *  *  *  *  command to be executed
```
So, for backing up data weekly at 12pm you could do:
```sh
0 12 * * 1 spotckup refresh && spotckup backup
```
To facilitate writing cronjobs, you should probably use [crontab guru](https://crontab.guru), an easy web editor for cron expressions.
**Remember** to always add the refresh command before any other command, otherwise the application will not be authorized to do any operation (the token expires in an hour).
