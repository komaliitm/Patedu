Running locally
---------------

Perform following operation:

    git clone https://pysu.visualstudio.com/DefaultCollection/_git/PYSU
    Edit UserEnv.bat for any non-default values.
    open PYSU.lnk
    Create postgres database 
    setup.bat
    python manage.py runserver
	
NOTE:
1.    Always access the django server on http://127.0.0.1:8000 for askbot to work.
2.    Don't skip creating admin user when syncdb runs.


Redis Dependencies:
1. server: https://github.com/rgl/redis/downloads download and install accordingly. Will be automating it in future.
		   After install go to install dir and run 'net start redis'. You might need to do it as Administrator. This will install a service that will start redis-server. This is a 1 time activity and service will take care of restart redis server on reboot.[Windows Specific]	

2. client: currently using redis-py which is implementation of redis protocol and is a fully functional redis client in python. "pip install" should have taken care of this.
