#!/bin/busybox sh
# load helper func in helpers/ dir

for helper_script in $MAN8S_INIT_DIR/lib-*.sh; do
    [ -e "$helper_script" ] || continue
    source "$helper_script"
    echo "Loaded helper script: $helper_script"
done
