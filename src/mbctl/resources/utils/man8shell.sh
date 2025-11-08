#!/bin/bash -e

# Usage: man8shell <name> [--network-only] -- <exec-command>
# exec-command is optional; default: /bin/sh

# If any argument is -h or --help, print help and exit 0
for _arg in "$@"; do
    case "$_arg" in
        -h|--help)
            cat <<'EOF'
Usage: man8shell <name> [--network-only] -- <exec-command>

Open a shell or run a command inside a systemd-nspawn container.

Positional arguments:
  name                Container name (service: systemd-nspawn@<name>)

Optional flags:
  --network-only      Only enter the network namespace (no PID/mount/etc.)
  --                  Separator indicating that following tokens form the command to execute
  -h, --help          Show this help message and exit

If no command is provided after --, the default command /bin/sh will be used.
EOF
            exit 0
            ;;
    esac
done

# Parse arguments: name, optional flag, then optional -- and command
network_only=0

[ -z "$1" ] && { echo "Usage: man8shell <name> [--network-only] -- <exec-command>" >&2; exit 1; }

name="$1"
shift

if [ "$1" = "--network-only" ]; then
    network_only=1
    shift
fi

# If next token is '--', consume it and treat remaining args as command
if [ "$1" = "--" ]; then
    shift
fi

# Remaining args (if any) are the command to execute inside the container
if [ "$#" -eq 0 ]; then
    exec_args=("/bin/sh")
else
    exec_args=("$@")
fi

mainpid=$(systemctl show -p MainPID --value "systemd-nspawn@$name")
[ -z "$mainpid" ] && { echo "Container service not found" >&2; exit 1; }

initpid=$(ps --ppid "$mainpid" -o pid= | awk 'NR==1{print $1}')
[ -z "$initpid" ] && { echo "Init PID not found" >&2; exit 1; }

if [ "$network_only" -eq 1 ]; then
    nsenter -t "$initpid" -n -- "${exec_args[@]}"
else
    nsenter -t "$initpid" -a -- "${exec_args[@]}"
fi
