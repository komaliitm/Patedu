#!/bin/bash

#ARGS
#arg1=$1

VHOSTNAME="www.analytics.dlpmcs.org"
VHOSTALIAS="analytics.dlpmcs.org"
ISDEMO=false
WSGIHOME=$HOME
WSGIUSER=$USER
WSGIGROUP=$USER
PROJECTDIR="dlpmcs/src/Patedu/patedu"


#Assign FQDN
FQDN="127.0.1.1 "$HOSTNAME".cloudapp.net "$HOSTNAME
sudo -- sh -c "echo $FQDN >> /etc/hosts"

#Install
sudo apt-get update
sudo apt-get install vim -y
sudo apt-get install python-virtualenv -y
sudo apt-get install git -y
sudo apt-get install apache2 -y
sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev -y
sudo apt-get install libpq-dev python-dev -y
sudo apt-get install postgresql postgresql-contrib -y
sudo apt-get install apache2-utils libexpat1 ssl-cert -y
sudo apt-get install libapache2-mod-wsgi -y
sudo apt-get install rabbitmq-server -y

#Prepare the postgres db
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'Doctl123';"
sudo -u postgres createdb dlpmcs_psqldb

#Enable Apache2 mpm worker mod
sudo a2dismod mpm_event
sudo a2enmod mpm_worker
sudo service apache2 restart

#Prepare the code base
mkdir dlpmcs
cd dlpmcs
virtualenv --no-site-packages venv
source venv/bin/activate

#Create git .netrc
touch ~/.netrc
chmod 0600 ~/.netrc
echo "machine github.com login komalvis007g@gmail.com password babboo@007" > ~/.netrc

#setup code base
mkdir src
cd src
git clone https://github.com/komaliitm/Patedu.git


#setup django plugins
cd Patedu
pip install Django==1.6.5
pip install -r requirements.txt
pip install psycopg2

#Add user and group for apache
sudo addgroup apache
sudo su -c "useradd apache -s /bin/bash -m -g apache"
sudo chpasswd << 'END'
apache:@ap@che#123
END

APACHEUSR=`grep -c 'APACHE_RUN_USER=www-data' /etc/apache2/envvars`
APACHEGRP=`grep -c 'APACHE_RUN_GROUP=www-data' /etc/apache2/envvars`
if [ APACHEUSR ]; then
    sudo sed -i 's/APACHE_RUN_USER=www-data/APACHE_RUN_USER=apache/' /etc/apache2/envvars
fi
if [ APACHEGRP ]; then
    sudo sed -i 's/APACHE_RUN_GROUP=www-data/APACHE_RUN_GROUP=apache/' /etc/apache2/envvars
fi
sudo chown -R apache:www-data /var/lock/apache2
sudo service apache2 restart

#Setup config files for WSGI User
rm -rf ~/tmp
mkdir ~/tmp
cp ~/dlpmcs/src/Patedu/resources/apache.host.composite.conf ~/tmp
cp ~/dlpmcs/src/Patedu/resources/celeryd ~/tmp

APACHE_VHOSTNAME=`grep -c '%VHOSTNAME%' ~/tmp/apache.host.composite.conf`
if [ APACHE_VHOSTNAME ]; then
	sed -i "s#%VHOSTNAME%#$VHOSTNAME#g" ~/tmp/apache.host.composite.conf
fi

APACHE_VHOSTALIAS=`grep -c '%VHOSTALIAS%' ~/tmp/apache.host.composite.conf`
if [ APACHE_VHOSTALIAS ]; then
	sed -i "s#%VHOSTALIAS%#$VHOSTALIAS#g" ~/tmp/apache.host.composite.conf
fi

APACHE_WSGIHOME=`grep -c '%WSGIHOME%' ~/tmp/apache.host.composite.conf`
if [ APACHE_WSGIHOME ]; then
	sed -i "s#%WSGIHOME%#$WSGIHOME#g" ~/tmp/apache.host.composite.conf
fi

APACHE_PROJECTDIR=`grep -c '%PROJECTDIR%' ~/tmp/apache.host.composite.conf`
if [ APACHE_PROJECTDIR ]; then
	sed -i "s#%PROJECTDIR%#$PROJECTDIR#g" ~/tmp/apache.host.composite.conf
fi

CELERYD_WSGIUSER=`grep -c '%WSGIUSER%' ~/tmp/celeryd`
if [ CELERYD_WSGIUSER ]; then
	sed -i "s#%WSGIUSER%#$WSGIUSER#g" ~/tmp/celeryd
fi

CELERYD_WSGIGROUP=`grep -c '%WSGIGROUP%' ~/tmp/celeryd`
if [ CELERYD_WSGIGROUP ]; then
	sed -i "s#%WSGIGROUP%#$WSGIGROUP#g" ~/tmp/celeryd
fi

CELERYD_WSGIHOME=`grep -c '%WSGIHOME%' ~/tmp/celeryd`
if [ CELERYD_WSGIHOME ]; then
	sed -i "s#%WSGIHOME%#$WSGIHOME#g" ~/tmp/celeryd
fi

CELERYD_PROJECTDIR=`grep -c '%PROJECTDIR%' ~/tmp/celeryd`
if [ CELERYD_PROJECTDIR ]; then
	sed -i "s#%PROJECTDIR%#$PROJECTDIR#g" ~/tmp/celeryd
fi

#Add demo.doctl.com virtual host
sudo cp ~/tmp/apache.host.composite.conf /etc/apache2/sites-available/
sudo a2ensite apache.host.composite
#Disable the default virtual host. #TODO later put a default error html page.
sudo a2dissite 000-default.conf
sudo a2dissite default-ssl.conf
sudo a2enmod rewrite
sudo sed -i '$a\ServerTokens ProductOnly' /etc/apache2/apache2.conf
sudo sed -i '$a\ServerSignature Off' /etc/apache2/apache2.conf
sudo service apache2 restart

#Add celery config file to defaults
sudo cp ~/tmp/celeryd /etc/default/

#Add celery init scripts
sudo cp ~/dlpmcs/src/Patedu/resources/celery-init/* /etc/init.d/
sudo chmod +x /etc/init.d/celeryd
sudo chmod +x /etc/init.d/celerybeat

#setup the db and migration 
cd ~/dlpmcs/src/Patedu/patedu
python manage.py syncdb
source migrate_script.sh
mkdir static/files
chmod 777 static/files

#start apache, celery, celerybeat
sudo service apache2 restart
 
sudo /etc/init.d/celeryd start
sudo /etc/init.d/celerybeat start

rm -rf ~/tmp