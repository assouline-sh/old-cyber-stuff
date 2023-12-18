#!/bin/bash

# Log file deletions and save a copy in a hidden directory, unless specified to not log with -n
deleted="/tmp/rm/.deleted/"
deletedlog="/tmp/rm/.deleted.log"

setup() {
	# Preserve original 'rm' and replace it with this script
	mv /bin/rm /bin/rm.orig
	cp test_del.sh /bin/rm

	# Create log directory and log file, allow everyone read + write and prevent deletion
	if [ ! -e "$deleted" ]; then
    	mkdir -p "$deleted"
    	touch "$deletedlog"
    	chmod -R 777 "/tmp/rm/"
    	chattr +a "$deletedlog"
	fi
}

# If first time running script, set up hidden directory and log file
if [ ! -x "/bin/rm.orig" ]; then
	setup
	exit 0
fi

# Save a copy of the deleted file and log the deletion if -n not given
if [ "$1" != "-n" ]; then
	for file in "$@"; do
    	cp -r "$file" "$deleted"
    	echo "$(date): ${USER}: $file" >> "$deletedlog"
	done
else
	shift
fi

# Delete the file
/bin/rm.orig "$@"

