sudo service apache2 stop
sudo /etc/init.d/celeryd stop
sudo /etc/init.d/celerybeat stop

sudo -u postgres dropdb dlpmcs_psqldb
sudo -u postgres createdb dlpmcs_psqldb

source ~/dlpmcs/venv/bin/activate
git fetch
git pull
pip install -r ../requirements.txt
python manage.py syncdb
source migrate_script.sh

sudo /etc/init.d/celeryd start
sudo /etc/init.d/celerybeat start
sudo service apache2 start