#!/bin/bash
# rget <url> <outfile> — fetch a reddit .rss through the ~1-req/45s limiter
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for i in 1 2 3 4 5 6; do
  c=$(curl -s -A "$UA" -o "$2" -w "%{http_code}" "$1")
  [ "$c" = "200" ] && [ -s "$2" ] && exit 0
  sleep 20
done
echo "reddit rss: giving up on $1 (last=$c)" >&2; exit 1
