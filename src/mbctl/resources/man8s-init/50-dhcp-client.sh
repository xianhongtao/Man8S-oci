#!/bin/busybox sh
# Minimal network initialization for BusyBox-only container

set -e

# 找出除了 lo 之外的第一个接口
MAN8S_HOST_IFACE="$(ip -o link show | awk -F': ' '{print $2}' | grep -v '^lo$' | sed 's/@.*//' | head -n1)"

export MAN8S_HOST_IFACE

if [ -z "$MAN8S_HOST_IFACE" ]; then
    echo "No non-loopback interface found"
    exit 1
fi

echo "Bringing up interface $MAN8S_HOST_IFACE"

ip link set dev "$MAN8S_HOST_IFACE" up
udhcpc -i "$MAN8S_HOST_IFACE" -q -n -t 3 -T 3

# 打印配置结果
echo "Final addresses:"
ip addr show dev "$MAN8S_HOST_IFACE"
ip route show
