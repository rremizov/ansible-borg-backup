.. sectnum::

Borg Backup
===========

Configure Borg Backup repository and create backups on schedule.

Features
--------

- Uses `BorgBackup`_ to create versioned, deduplicated and encrypted backups.

Requirements
------------

- Debian

Role Vars
---------

``borg_backup``
~~~~~~~~~~~~~~~

Configuration of the Borg repositories. See the schema in the examples below.

Example
-------

.. code:: yaml

    borg_backup:
      - directory: / # The directory to backup
        borg_repository: /var/backups/root/ # Path to the borg repository.
        borg_passphrase: passphrase # BEWARE! Stored in plain text in the backup script! Optional.
        borg_exclude: # Optional.
          - /var/backups
          - /boot
          - /dev
          - /home
          - /proc
          - /run
          - /tmp
          - /sys
        cron_month: "*"
        cron_weekday: "*"
        cron_day: "*"
        cron_hour: "0"
        cron_minute: "0"
        supress_mail_on_success: no # Use chronic to supress unwanted mail from cron. Default: yes.
        retention_hourly: 24 # Number of hourly archives to keep.
        retention_daily: 30 # Number of daily archives to keep.
        retention_weekly: 12 # Number of weekly archives to keep.
        retention_monthly: 12 # Number of monthly archives to keep.
        retention_yearly: 3 # Number of yearly archives to keep.

.. _BorgBackup: https://github.com/borgbackup