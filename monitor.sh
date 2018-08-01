#!/bin/bash
function cleanup {
	tail -n+2 temp.csv >> log.csv
	rm temp.csv
}
python temp_monitor.py
trap cleanup EXIT
