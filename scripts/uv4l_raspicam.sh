
#!/bin/sh
### BEGIN INIT INFO
# Provides:          uv4l_raspicam
# Required-Start:    udev
# Required-Stop:
# Default-Start:     S
# Default-Stop:
# X-Interactive:
# Description: UV4L Raspberry CSI Userspace Camera Driver
# Short-Description:    Userspace Camera Driver
### END INIT INFO

PATH='/sbin:/bin:/usr/bin'

NAME=uv4l_raspicam.sh
UV4L=/usr/bin/uv4l
FIND_PID="ps -eo pid,args | grep uv4l | grep '\--driver raspicam' | awk '{print \$1}'"

RET=0

. /lib/lsb/init-functions

kill_pid () {
    PID=$(eval $FIND_PID)
    if [ ! -z $PID ]; then
        kill $PID
        PID=$(eval $FIND_PID)
        if [ ! -z $PID ]; then
            sleep 3
            kill -9 $PID
        fi
    fi
}

case "$1" in
    start|reload|restart|force-reload)
    	kill_pid
	log_daemon_msg "Starting UV4L Raspberry CSI Camera Driver" "uv4l"
	echo
    	$UV4L uv4l  --driver raspicam --auto-video_nr --encoding yuv420 --nopreview --shutter 10000 
    	RET=$?
        ;;
    stop)
    	kill_pid
    	RET=$?
        ;;
    status)
        ;;
    *)
    	log_failure_msg "Usage: /etc/init.d/$NAME {start|stop|restart}"
    	RET=1
        ;;
esac

exit $RET

:
