#!/bin/bash
#-*- encoding: utf-8 -*-

# Apache の再起動を妨げる PID ファイルを削除する
rm -f /run/apache/apache2.pid # https://stackoverflow.com/a/41295226/13301046
rm -f /var/run/apache2/apache2.pid # https://blog.paranoidpenguin.net/2017/09/downtime-due-to-apache-ah00060/

apache2ctl -D FOREGROUND &
PID1=$!
runuser \
    --user diagnose-ai \
    -- python3 -u /var/www/maff_ai/src/model/daemon.py &
PID2=$!

# コンテナ停止時は Apache を graceful stop する
# (https://httpd.apache.org/docs/2.4/stopping.html#gracefulstop)
# これが無いと、コンテナ内のプロセスは毎回 SIGKILL される
# (https://docs.docker.com/compose/faq/#why-do-my-services-take-10-seconds-to-recreate-or-stop)
trap "kill -SIGWINCH ${PID1} && kill -SIGTERM ${PID2}" SIGTERM
wait $PID1 $PID2

