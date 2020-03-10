./tools/backup.sh --rest --plugin --postgresql --wordpress -o /mnt/data/backups -z

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

if [ -f $parent_path/email.conf ]; then
	. $parent_path/email.conf
	file=$( date +%Y%m%d )
	fdate=$( date +%d/%m/%Y )
	echo "Automated email: backup taken on $fdate attached" | mailx -s '[Automated] Backup $fdate' $email -a "From: $email" -A backup/$file.tar.gz
fi
