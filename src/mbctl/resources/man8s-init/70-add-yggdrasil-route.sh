#!/bin/busybox sh
# Configure Yggdrasil IP address if MAN8S_YGGDRASIL_ADDRESS is set

# 此脚本自动完成容器的Man8S网络配置，具体请参考 README 中有关Man8S网络配置的讲解。

mkdir -p /etc/iproute2
TABLE_FILE="/etc/iproute2/rt_tables"
ENTRY="199 ygg"

# 添加路由表项，如果路由表已存在则不要添加。
if ! grep -qE "^${ENTRY}\$" "$TABLE_FILE" 2>/dev/null; then
    echo "$ENTRY" >> "$TABLE_FILE"
fi

GET_LINK_INFO() {
    # 获取接口上 fc00:: 开头的 IPv6 地址（取第一个）
    SRC_ADDR=$(ip -6 addr show dev "$MAN8S_HOST_IFACE" \
        | awk '/inet6 fc00::/{print $2}' \
        | cut -d/ -f1 \
        | head -n1)

    # 获取现有 default via 的网关地址（fe80::开头）
    GW_ADDR=$(ip -6 route show dev "$MAN8S_HOST_IFACE" default \
        | awk '/via fe80::/{for(i=1;i<=NF;i++){if($i=="via"){print $(i+1); exit}}}')

    # 获取 default route metric（保留原路由的 metric）
    METRIC=$(ip -6 route show dev "$MAN8S_HOST_IFACE" default \
        | awk '/metric/{for(i=1;i<=NF;i++){if($i=="metric"){print $(i+1); exit}}}')

    if [ -z "$SRC_ADDR" ] || [ -z "$GW_ADDR" ] || [ -z "$METRIC" ]; then
        echo "无法获取必要的网络信息"
        return 1
    fi
}

# 设置网络信息。反复执行命令直到获取所有网络的信息，才能开始后面的网络设置。
DO_UNTIL_SUCCESS GET_LINK_INFO

# 需要先修改一下当前SLAAC自动配置的默认路由的出口源地址，将其设置为本机的fc00::内网地址。
DO_UNTIL_SUCCESS ip -6 route change default via "$GW_ADDR" dev "$MAN8S_HOST_IFACE" metric "$METRIC" src "$SRC_ADDR"

# 添加 Yggdrasil 专用路由表的默认路由
DO_UNTIL_SUCCESS ip addr add "$MAN8S_YGGDRASIL_ADDRESS/64" dev "$MAN8S_HOST_IFACE" noprefixroute

# 添加路由规则，将访问 200::/7 的流量走 ygg 路由表
DO_UNTIL_SUCCESS ip -6 route add "$MAN8S_YGGDRASIL_ADDRESS/64" dev "$MAN8S_HOST_IFACE" src "$MAN8S_YGGDRASIL_ADDRESS" table 199
DO_UNTIL_SUCCESS ip -6 route add 200::/7 via "$GW_ADDR" dev "$MAN8S_HOST_IFACE" src "$MAN8S_YGGDRASIL_ADDRESS" table 199
DO_UNTIL_SUCCESS ip -6 rule add to 200::/7 lookup 199 priority 100
