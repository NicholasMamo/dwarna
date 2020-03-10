#!/usr/bin/env bash

./tools/backup.sh --rest --plugin --postgresql --wordpress -o /mnt/data/backups -z

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

if [ -f $parent_path/email.conf ]; then
	. $parent_path/email.conf
	file=$( date +%Y%m%d )
	fdate=$( date +%d/%m/%Y )
	mailx -s "[Automated] Backup $fdate" $to -a "From: $to" -A backup/$file.tar.gz
fi
