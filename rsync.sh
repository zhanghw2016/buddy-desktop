#!/bin/bash
#
# Copyright (C) 2019 Yunify Inc.
#
# Script to rsync pitrix-desktop code 

# 默认关闭bash调试模式
# set -x
SCRIPT=$(readlink -f $0)
CWD=$(dirname ${SCRIPT})

# 初始化安装必要参数变量
#REMOTE_IPS="192.168.13.205 192.168.13.203 192.168.13.228 192.168.13.12"
#REMOTE_IPS="172.31.47.26 172.31.47.27"
#REMOTE_IPS="192.168.13.164 192.168.13.202"
#REMOTE_IPS="192.168.13.205"
#REMOTE_IPS="192.168.13.72 192.168.13.157"
#REMOTE_IPS="172.31.45.26"
REMOTE_IPS="10.11.13.16"
#REMOTE_IPS="192.168.13.205"
#REMOTE_IPS="192.168.13.79"
#REMOTE_IPS="172.31.47.26 172.31.47.27"

function usage()
{
    echo "Usage:"
    echo "    rsync.sh"
    echo "Example:"
    echo "    rsync.sh"
}

if [[ "x$1" == "x-h" ]] || [[ "x$1" == "x--help" ]]; then
    usage
    exit 1
fi

function prepare_install()
{  

	echo "Enter the necessary parameters for installation"
	
	#REMOTE_IP
	while [[ "${REMOTE_IPS}" == "" ]]
	do
		echo -ne "${YELOW}Enter REMOTE_IP(desktop-server ip):${RES}"
		read REMOTE_IP
		if [[ "${REMOTE_IPS}" != "" ]]; then
			echo "REMOTE_IPS=${REMOTE_IPS}"
			break
		else
			echo -e "${YELOW}Error:The REMOTE_IPS [${REMOTE_IPS}] you provide is  invalid,please check it!${RES}"
			continue
		fi
	done
}

function rsync_pitrix_desktop()
{
	echo "rsync_pitrix_desktop"
	echo "REMOTE_IPS=${REMOTE_IPS}"
	cd ${CWD}
	for REMOTE_IP in ${REMOTE_IPS}
	do
	    echo "rsync to REMOTE_IP:${REMOTE_IP}"
        rsync -rtv ./src/common/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop-common/common/
        rsync -rtv ./src/agent/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/agent/
        rsync -rtv ./src/desktop/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/desktop/
        rsync -rtv ./src/dispatch/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/dispatch/
        rsync -rtv ./src/push/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/push/
        rsync -rtv ./src/resource/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/resource/
        rsync -rtv ./src/scheduler/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/scheduler/
        rsync -rtv ./src/terminal/ root@${REMOTE_IP}:/pitrix/lib/pitrix-desktop/terminal/
        rsync -rtv ./conf/desktop/desktop_agent.yaml root@${REMOTE_IP}:/pitrix/conf/desktop/desktop_agent.yaml

        #restart REMOTE_IP desktop_server
        ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart desktop_server"

    ##	#restart REMOTE_IP dispatch_server
        ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart dispatch_server"
    #
    ##	restart REMOTE_IP desktop_scheduler
    #	ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart desktop_scheduler"
    ##
    ##	#restart REMOTE_IP desktop_agent
    	ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart desktop_agent"
    ##
    #	#restart REMOTE_IP desktop_push
#    	ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart desktop_push"
    ##
    ##	#restart REMOTE_IP terminal_server
    #   ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart terminal_server"

    #	#restart REMOTE_IP desktop_server
    #	ssh -o StrictHostKeyChecking=no root@${REMOTE_IP} "supervisorctl restart all"
    done
}

mkdir -p /pitrix/log/install
log_file="/pitrix/log/install/rsync_pitrix_desktop.log"
if [ -f ${log_file} ]; then
    echo "" > ${log_file}
fi

function log()
{
    msg=$*
    date="$(date +'%Y-%m-%d %H:%M:%S')"
    echo "${date} ${msg}" >> ${log_file}
}


function SafeExecFunc()
{
    local func=$1
    log "Execing the function [${func}] ..."
    ${func} >>${log_file} 2>&1
    if [ $? -eq 0 ]; then
        echo -n "OK." && echo ""
        log "Exec the function [${func}] OK."
    else
        echo -n "Error!" && echo ""
        log "Exec the function [${func}] Error!"
        exit 1
    fi
}

date="$(date +'%Y-%m-%d %H:%M:%S')"
echo -n "${date} Preparing install... "
prepare_install


date="$(date +'%Y-%m-%d %H:%M:%S')"
echo -n "${date} rsyncing pitrix desktop..... "
SafeExecFunc rsync_pitrix_desktop
