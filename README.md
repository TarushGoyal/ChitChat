# ChitChat / Hemlo
## real time chatting and communication

### First Timers:

1) git clone this repo in an empty directory
2) make a virtual environemnt in that directory using : 
	
	$python3 -m venv env

3) start the virtual environment using :

	$source env/bin/activate\

	you can check that virtual environemnt is started by doing :

	$which python3

4) install flask and its submodules using :

	$python3 -m pip install -r ChitChat/requirements.txt

5) Now set environment variable FLASK_APP 

	#export FLASK_APP=ChitChat

6) Initialize the app

	$python3 \
	_from ChitChat import db, create_app_\
	_db.create_all(app=create_app())_ # ignore warnings\
	_exit()_

7) Now you are ready to start the server

	$flask run

### Constributors:

1) if you are making a "discussed" change (approved by other members and known to work for sure) then directly commit on the master branch.

2) If you are experimenting with a feature / implementing a long shot feature make your own branch and only when it is tested merge with master branch.

3) preferable branch name = featureName_myName eg. invitation_anuj

4) **Do not push env / database**

### Using sqlite:

1) $cd ChitChat

2) $sqlite3\
		sqlite> .open db.sqlite\
		sqlite> .tables 

3) rest is same as postgres.
