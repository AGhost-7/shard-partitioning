#!/bin/bash

set -e

# This file overrides the builtin entrypoint to allow dynamic configuration
# of the mysql server through environment variables.

if [ -z "$MYSQL_SERVER_ID" ]; then
	echo 'MYSQL_SERVER_ID is a required environment variable'
	exit 1
fi

cat > /etc/mysql/mariadb.conf.d/shard.cnf <<CONFIG
[mysqld]
server-id=$MYSQL_SERVER_ID
CONFIG

sleep 2

exec /docker-entrypoint.sh "$@"
