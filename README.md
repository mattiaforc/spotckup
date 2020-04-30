### Extra - `cron` job for automatic backups

You may want to do the backup on a regular basis by using `cron`.
`cron` is a time-based job scheduler in Unix-like computer operating systems which allows flexible and powerful scheduling.

First of all, if you don't have `cron` installed, run
```sh
sudo apt-get update
sudo apt-get install cron 
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
So, for backing up data weekly at noon you could do:
```sh
0 12 * * 1 spotckup refresh && spotckup backup
```
To facilitate writing cronjobs, you should probably use [crontab guru](https://crontab.guru), an easy web editor for cron expressions.
**Remember** to always add the refresh command before any other command, otherwise the application will not be authorized to do any operation.
