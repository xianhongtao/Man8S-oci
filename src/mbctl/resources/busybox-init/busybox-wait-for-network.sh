#!/bin/sh
# Wait for network connectivity

# 配置：可修改重试间隔（秒）
RETRY_INTERVAL=${RETRY_INTERVAL:-1}

# 目标主机
HOST1="1.1.1.1"
HOST2="mirrors6.tuna.tsinghua.edu.cn"

# 确认 MAN8S_YGGDRASIL_ADDRESS 已设置
if [ -z "${MAN8S_YGGDRASIL_ADDRESS-}" ]; then
  BUSYBOX_RUN printf '错误: 环境变量 MAN8S_YGGDRASIL_ADDRESS 未设置。\n请先 export MAN8S_YGGDRASIL_ADDRESS="你要检测的地址"\n'
  return 2
fi

# 简单的可用性检测：优先用 BUSYBOX_RUN ping 单次检测，失败则退回到 HTTP(S) 头请求（curl/wget）
check_host() {
  host=$1

  # try BUSYBOX_RUN ping -c 1 (most systems)
  if command -v BUSYBOX_RUN ping >/dev/null 2>&1; then
    # 使用 -c 1 发一个包，-W 1 作为超时（部分系统支持 -w 或 -W）
    BUSYBOX_RUN ping -c 1 -W 1 "$host" >/dev/null 2>&1 && return 0
    # 如果 BUSYBOX_RUN ping 失败，再尝试 curl / wget
  fi

  return 1
}

# 检查本机是否拥有指定地址（优先 ifconfig，其次 ip addr）
check_local_addr() {
  addr="$1"
  if command -v ifconfig >/dev/null 2>&1; then
    ifconfig 2>/dev/null | grep -qF "$addr" && return 0
  fi

  return 1
}

# 捕获 Ctrl-C 使脚本优雅退出
trap 'BUSYBOX_RUN printf "\n中断，退出。\n"; return 130' INT

BUSYBOX_RUN printf '开始检测：\n  - %s\n  - %s\n  - 本机地址 %s\n每 %s 秒重试一次，直到三项全部通过。\n\n' "$HOST1" "$HOST2" "$MAN8S_YGGDRASIL_ADDRESS" "$RETRY_INTERVAL"

while :; do
  now="$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || BUSYBOX_RUN printf '%s' "$(date)")"
  BUSYBOX_RUN printf '[%s] 检测中: %s ... ' "$now" "$HOST1"
  if check_host "$HOST1"; then
    BUSYBOX_RUN printf 'OK\n'
  else
    BUSYBOX_RUN printf 'FAIL\n'
    BUSYBOX_RUN sleep "$RETRY_INTERVAL"
    continue
  fi

  BUSYBOX_RUN printf '[%s] 检测中: %s ... ' "$now" "$HOST2"
  if check_host "$HOST2"; then
    BUSYBOX_RUN printf 'OK\n'
  else
    BUSYBOX_RUN printf 'FAIL\n'
    BUSYBOX_RUN sleep "$RETRY_INTERVAL"
    continue
  fi

  BUSYBOX_RUN printf '[%s] 检查本机地址: %s ... ' "$now" "$MAN8S_YGGDRASIL_ADDRESS"
  if check_local_addr "$MAN8S_YGGDRASIL_ADDRESS"; then
    BUSYBOX_RUN printf 'FOUND\n'
  else
    BUSYBOX_RUN printf 'NOT FOUND\n'
    BUSYBOX_RUN sleep "$RETRY_INTERVAL"
    continue
  fi

  # 如果能运行到这里，三项都通过
  BUSYBOX_RUN printf '\n网络正常。\n'
  return 0
done
