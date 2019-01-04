#!/bin/bash

repository_owner="bodiroga"
name="marantz-homie-controller"
user="pi"

## Making sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root" 1>&2
   exit 1
fi


## Installing the required programs
echo -e '\nInstalling the required programs...'
apt update >/dev/null
apt --assume-yes install git python3 python3-dev python3-pip python3-venv >/dev/null


## Cloning the github repository
cd /tmp
if [ -d "$name" ]; then
	echo -e "\nThe github repository already exists, let's make a 'git pull'..."
	cd $name
	git pull
else
	echo -e "\nCloning the github repository..."
	git clone https://github.com/$repository_owner/$name.git
	cd $name
fi


## Moving the program files to the installation directory
echo -e '\nCopying the program to the installation (/opt/homie-marantz-controller) folder...'
cp -rf $name /opt


## Creating and activating the virtual environment
echo -e '\nCreating the virtual environment...'
cd /opt/$name
python3 -m venv .env


## Installing the required python libraries
echo -e '\nInstalling the required python libraries...'
/opt/$name/.env/bin/pip3 install -r /tmp/$name/requirements.txt > /dev/null


## Adding the start script file
echo -e '\nAdding the start script file...'
cp -rf /tmp/$name/systemd/$name.service /etc/systemd/system/$name.service
systemctl daemon-reload
systemctl enable $name.service


## Fixing user permissions
echo -e '\nFixing user permissions...'
chown -R $user:$user /opt/$name


## Removing the git repository
echo
read -p "Do you want to remove the git repository from your computer (y/N)? " choice
case "$choice" in
  y|Y|s|S ) echo -e "Deleting the git repository..."; rm -rf /tmp/$name;;
  * ) echo -e "Keeping the git repository...";;
esac


## Start the program
echo
read -p "Do you want to start the program now (Y/n)? " choice
case "$choice" in
  n|N ) echo -e "You can start the program typing 'systemctl start $name.service'";;
  * ) echo -e "Starting the program..."; systemctl start $name.service;;
esac


## Done
echo -e "\nDone."
