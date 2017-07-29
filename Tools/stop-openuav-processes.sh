#!/bin/bash 
kill $(ps aux | grep ros | awk '{print $2}') && ~/gzweb/stop_gzweb.sh
