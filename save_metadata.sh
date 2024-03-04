#!/bin/sh
#
# Simple script to preserve metadata of files into text file
# Part of PublicTrashCan
#
# (c) Mikhail Lebedinets, 2024
#

set -e

DB_FILENAME='./metadata.txt'
SAVE_DIR='./Projects'

START_DATE="$(date +'%Y-%m-%dT%H:%M:%SZ')"

cd "$(dirname "$0")"

host_os="$(uname)"

if [ "$host_os" != 'Darwin' ] && [ "$host_os" != 'Linux' ]; then
    echo 'Error: This script works only on Mac OS X or Linux!' 1>&2
    exit 1
fi

old_metadata_db=""

if [ -f "$DB_FILENAME" ]; then
    old_metadata_db="$(cat $DB_FILENAME)"
    echo "$old_metadata_db" > "$DB_FILENAME.bak"
fi

unix_to_iso8061() {
    if [ "$host_os" = 'Darwin' ]; then
        iso_date="$(date -u -r "$1" +'%Y-%m-%dT%H:%M:%SZ')"
    elif [ "$host_os" = 'Linux' ]; then
        # afaik xfs does not support file birth date property
        iso_date="$(date -u -d @"$1" +'%Y-%m-%dT%H:%M:%SZ')"
    fi

    echo "$iso_date"
}

get_brithdate() {
    if [ "$host_os" = 'Darwin' ]; then
        birthdate="$(stat -f "%B" "$1")"
    elif [ "$host_os" = 'Linux' ]; then
        birthdate="$(stat -c "%W" "$1")"
    fi

    echo "$birthdate"
}

get_mtime() {
    if [ "$host_os" = 'Darwin' ]; then
        mtime="$(stat -f "%m" "$1")"
    elif [ "$host_os" = 'Linux' ]; then
        mtime="$(stat -c "%Y" "$1")"
    fi

    echo "$mtime"
}

save_metadata() {
    printf '%s: ' "$1"

    if [[ "$old_metadata_db" = *"$1"* ]]; then
      echo "Already saved"
      return
    fi

    printf 'New File\n - '

    birthdate="$(get_brithdate "$1")"
    iso_birthdate="$(unix_to_iso8061 "$birthdate")"
    printf 'Birth: %s\t' "$iso_birthdate"

    mtime="$(get_mtime "$1")"
    iso_mtime="$(unix_to_iso8061 "$mtime")"
    printf 'MTime: %s' "$iso_mtime"

    echo "{\"file\":\"$1\", \"saved\": \"$START_DATE\", \"birth\": \"$iso_birthdate\", \"mtime\": \"$iso_mtime\"}" >> "$DB_FILENAME"

    printf '\n----------\n'
}


files="$(find "$SAVE_DIR" -type f ! -name '.DS_Store')"

if [ -z "$files" ]; then
    echo "Error: Save directory is empty!"
    exit 1
fi

echo "$files" | while read file; do
    save_metadata "$file"
done

echo "Done!"
