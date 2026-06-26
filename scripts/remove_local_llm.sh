#!/usr/bin/env bash
set -euo pipefail

PORT=${LLAMA_PORT:-10124}

mapfile -t pids < <(pgrep -f "llama-server" || true)

if [ "${#pids[@]}" -eq 0 ]; then
    echo "No llama-server processes running."
    exit 0
fi

echo "Stopping llama-server processes: ${pids[*]}"
kill "${pids[@]}" 2>/dev/null || true

for _ in $(seq 1 10); do
    mapfile -t remaining < <(pgrep -f "llama-server" || true)
    if [ "${#remaining[@]}" -eq 0 ]; then
        echo "Stopped local LLM."
        exit 0
    fi
    sleep 0.5
done

mapfile -t remaining < <(pgrep -f "llama-server" || true)
if [ "${#remaining[@]}" -gt 0 ]; then
    echo "Force-killing remaining llama-server processes: ${remaining[*]}"
    kill -9 "${remaining[@]}" 2>/dev/null || true
    sleep 1
fi

mapfile -t remaining < <(pgrep -f "llama-server" || true)
if [ "${#remaining[@]}" -gt 0 ]; then
    echo "Warning: some llama-server processes could not be killed:" >&2
    ps -o pid,stat,etime,cmd -p "$(IFS=,; echo "${remaining[*]}")" >&2 || true
    echo "Processes in D state are stuck in the kernel and usually require reboot." >&2
    exit 1
fi

if ss -ltn "( sport = :$PORT )" | grep -q LISTEN; then
    echo "Warning: port $PORT is still busy:" >&2
    ss -ltnp "( sport = :$PORT )" >&2 || true
    exit 1
fi

echo "Stopped local LLM."
