#!/bin/sh

set -e +x

export $(grep -e "^LAYER=" -e "^DATABASE_[A-Z]\+=" .env)

datestamp=`date +%Y%m%d-%H%M%S`
dumpdir=./pgdumps
mkdir -p $dumpdir

docker compose exec "${DATABASE_HOST}" \
	pg_dump \
		--format=custom --compress=9 \
		--no-owner --no-acl \
		--user="${DATABASE_USER}" "${DATABASE_NAME}" \
	> "$dumpdir/${LAYER}-$datestamp.dump"

find "$dumpdir" -type f -name '*.dump' -mtime +7 -print0 | \
	xargs -0 -r /bin/rm -f
