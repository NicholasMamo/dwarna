#!/usr/bin/env bash

source /var/www/dwarna/venv/bin/activate
/var/www/dwarna/rest/deliver.py >> /var/log/mail/$( date +%Y%m%d ).log
deactivate
