#!/usr/bin/env bash

DEBUG_PARAMS=""
if [ "${DEBUG}" = "1" ]; then
  DEBUG_PARAMS="-m pdb"
fi


# --org-repo is case sensitive

time python ${DEBUG_PARAMS} \
    ./ghreport/main.py \
    --report-name inlyse-dashboard \
    --report-title "Inlyse Dashboard Monthly Report" \
    --org-repo inlyse/inlyse-Dashboard \
    --author xmnlab \
    --author Someone-Somewhere \
    --author hsouna \
    --author NKKFu \
    --author jloehel \
    --output-format md \
    --output-dir "/tmp/ghreport"
