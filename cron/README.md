These files can be used to start an automated `cron` job for `lyz`. You will need to fill them in with the appropriate information for use on your system.

## `cron` Cheatsheet

start cron job from file

```
crontab run.job
```

check cron jobs

```
crontab -l
```

edit the current cron job file

```
crontab -e
```

remove the cron job

```
crontab -r
```

### Examples [[source]](https://alvinalexander.com/linux/unix-linux-crontab-every-minute-hour-day-syntax)

more help [here](https://crontab.guru/)

```
# field #   meaning        allowed values
# -------   ------------   --------------
#    1      minute         0-59
#    2      hour           0-23
#    3      day of month   1-31
#    4      month          1-12 (or names, see below)
#    5      day of week    0-7 (0 or 7 is Sun, or use names)

```

```
# every minute
* * * * * command

# every hour, on the hour
0 * * * * command

# every hour, at :05
5 * * * * command

# every 5 minutes
*/5 * * * * command

# once every 2 hours
0 */2 * * * command

# every hour Thurs, Fri, Sat.
0 * * * 4,5,6 command
```
