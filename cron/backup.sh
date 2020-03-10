#!/usr/bin/env bash

./tools/backup.sh --rest --plugin --postgresql --wordpress -o /mnt/DATA/backups -z

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

if [ -f $parent_path/email.conf ]; then
	. $parent_path/email.conf
	file=$( date +%Y%m%d )
	fdate=$( date +%d/%m/%Y )
	echo "" | mailx -s "[Automated] Backup $fdate" $to -a "From: $to" -A /mnt/DATA/backups/$file.tar.gz
fi
