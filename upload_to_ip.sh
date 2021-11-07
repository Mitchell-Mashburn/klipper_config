#!/bin/bash

usage() {
  cat << EOF # remove the space between << and EOF, this is due to web plugin issue
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [ip]

Choose which Gigabot uploading config files to
Upload klipper config files to RaspberryPi

Available options:

-h, --help      Print this help and exit
ip		Last octet of the machine to upload to. Assumes change FIRST_THREE_OCTETS to change ip octet.
EOF
  exit
}

if [ -z "$1" ]
then
	usage
fi

FIRST_THREE_OCTETS="10.1.10."

NEW_FILE="gigabot_steppers.cfg"
read -p "Enter Gigabot Size: (1)Regular (2)XLT (3)Terabot (4)Exabot: " model; echo
./get_bedsize.sh $model

echo Uploading to IP $FIRST_THREE_OCTETS$1
scp -r {./*.cfg,./*.conf,./get_serial.sh} pi@$FIRST_THREE_OCTETS$1:~/klipper_config/
rm $NEW_FILE

ssh pi@$FIRST_THREE_OCTETS$1 "./klipper_config/get_serial.sh"

