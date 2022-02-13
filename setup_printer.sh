#!/bin/bash

set -e 

usage() {
  cat << EOF # remove the space between << and EOF, this is due to web plugin issue
Usage: $(basename "${BASH_SOURCE[0]}") -b [bedsize] [-d | -uart | -internal]

[bedsize]
    Enter the following to create a gigabot_stepper.cfg file for sizes:
    1) Regular
    2) XLT
    3) Terabot
    4) Exabot

[-d | -uart | -internal]
    -d         Generate a gigabot_dev.cfg file for re:3D's SDK
    -uart      Use uart instead of USB for communication
    -internal  Set up mainsail to point to web_beta (Prerelease)
EOF
  exit
}

if [ -z "$1" ]
then
	usage
fi

PWD="$(cd "$(dirname "$0")" && pwd)"
TMPL_PWD=$PWD/templates

$PWD/get_bedsize.sh $1

if [[ -n "$2" && $2 == "-d" ]]
then
    echo Setting up for Development Pi
    cp $TMPL_PWD/gigabot_dev.cfg.tmpl $PWD/gigabot_dev.cfg
else
    echo "" > $PWD/gigabot_dev.cfg
fi

if [[ -n "$2" && $2 == "-uart" ]]
then
    $PWD/get_serial.sh -uart
else
    $PWD/get_serial.sh
fi

if [[ ! -f $PWD/gigabot_save_variables.cfg ]]
then
    cp $TMPL_PWD/gigabot_save_variables.cfg.tmpl $PWD/gigabot_save_variables.cfg
fi

if [[ ! -f $PWD/gigabot_standalone_config.cfg ]]
then
    cp $TMPL_PWD/gigabot_standalone_config.cfg.tmpl $PWD/gigabot_standalone_config.cfg
fi

cp $TMPL_PWD/moonraker.conf.tmpl $PWD/moonraker.conf
