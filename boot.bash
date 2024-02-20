#!/bin/bash

cleanup() {
    echo "Cleaning up..."
    kill -INT "${background_pids[@]}"
    exit 1
}

trap cleanup SIGINT

tcpdump -i any -w /tcpdump/dump.pcap &
background_pids+=($!)
/usr/local/bin/python3 client.py &
background_pids+=($!)

# Wait for background commands to finish
wait ${background_pids[@]}

