#!/usr/bin/env bash

# Execute this script to search for all directories matching the input arguments
# e.g. ./search.sh -l ./notebooks/logs/ "density_final: 0.45" "r_cut: 3.0"

function err_n_die() {
    echo "Script usage: search.sh -l LOG_DIR [search strings]"
    echo "example: ./search.sh -l ./notebooks/logs/ \"density_final: 0.45\" \"r_cut"
    exit 1
}

while getopts 'l:h' OPTION; do
    case "$OPTION" in
        l)
            LOG_DIR="${OPTARG}"
            ;;
        h)
            err_n_die
            ;;
        *)
            err_n_die
            ;;
    esac
done

if [ -z $LOG_DIR ] || [ "$#" -lt 3 ]; then
    err_n_die
fi

find_command="find notebooks/logs/ -type f -name \"parameters.txt\" -exec grep -l \"${3}\" {} \;"

for (( i=4; i<=$#; i+=1 )); do
    find_command+=" | xargs grep -l \"${!i}\""
done

find_command+=" | xargs -I {} dirname {} | sort"

echo "$find_command"
eval "$find_command"
