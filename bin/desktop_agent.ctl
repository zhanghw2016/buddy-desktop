#! /bin/sh

# the program name defined in /etc/supervisord.conf
NAME=desktop_agent

set -e

case "$1" in
  start)
        supervisorctl start $NAME
    ;;
  stop)
        supervisorctl stop $NAME
    ;;
  status)
        supervisorctl status $NAME
    ;;
  restart|force-reload)
        supervisorctl restart $NAME
    ;;
  *)
    N=$0
    echo "Usage: $N {start|stop|status|restart}" >&2
    exit 1
    ;;
esac

exit 0
