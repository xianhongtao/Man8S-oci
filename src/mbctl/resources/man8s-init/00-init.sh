#!/bin/busybox sh
# A minimal init script for BusyBox-based containers.
MAN8S_INIT_DIR="/man8s-init"
MAX_RETRY_TIMES=10
RETRY_INTERVAL_SECONDS=1

source $MAN8S_INIT_DIR/*load-helpers.sh
source $MAN8S_INIT_DIR/*load-envs.sh
source $MAN8S_INIT_DIR/*copy-protected-dirs.sh
source $MAN8S_INIT_DIR/*dhcp-client.sh
source $MAN8S_INIT_DIR/*add-yggdrasil-route.sh
source $MAN8S_INIT_DIR/*connection-check.sh
source $MAN8S_INIT_DIR/*application.sh
