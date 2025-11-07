DO_UNTIL_SUCCESS() {
    max_attempts=${MAX_RETRY_TIMES:-5}
    count=0
    while [ $count -lt $max_attempts ]; do
        "$@" && return 0
        count=$((count + 1))
        sleep ${RETRY_INTERVAL_SECONDS:-1}
    done
    echo "命令在 ${max_attempts} 次尝试后仍未成功。" >&2
    return 1
}
