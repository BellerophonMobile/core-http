#!/bin/sh

set -x -e

./corecli.py session new test tom

./corecli.py session list

./corecli.py session 1 node new wlan wlan0 100 100 0
./corecli.py session 1 node new default n0 50 200 0
./corecli.py session 1 node new default n1 250 200 0
./corecli.py session 1 node list

./corecli.py session 1 node 1 position 75 350 0

./corecli.py session 1 node 1 netif new 0 10.0.0.1/24
./corecli.py session 1 node 2 netif new 0 10.0.0.2/24

./corecli.py session 1 state instantiation

./corecli.py session 1 node 1 execute ip route add default dev eth0
./corecli.py session 1 node 2 execute ip route add default dev eth0

./corecli.py session list

./corecli.py session 1 node 1 info
./corecli.py session 1 node 2 info

#curl -N http://localhost:8080/sessions/1/nodes/1/events
