== Installation ==

Assumptions:
* You have precise pangolin running
* You have installed git and SSH

Steps:
* Get the code
** $ git clone ssh://ubuntu@akorn.org/~/git/akorn_search.git
* Install required ubuntu packages
** $ sudo apt-get install $(cat akorn_search/UBUNTU_PACKAGES)
* Install virtualenvwrapper
** $ sudo easy_install pip
** $ sudo pip install virtualenv virtualenvwrapper
** $ mkdir ~/.virtualenvs
** Add the following to ~/.bashrc

export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
export PIP_VIRTUALENV_BASE=$WORKON_HOME

** $ source ~/.bashrc 
* Build a virtual environment to run the code
** $ mkvirtualenv -a ~/akorn_search/ -r akorn_search/REQUIREMENTS.txt akorn
* Get a couchdb dump, so you have test data to play with
* Set up couchdb
** $ sudo update-rc.d couchdb enable
** $ sudo service couchdb start
* Get a dump from the server and load it into your local couchdb
** $ workon akorn
** (akorn) $ fab load_dumps
** (akorn) $ couchdb-load --input=~/fulldump http://localhost:5984/store

# Instructions to get full text search working, using couchdb-lucene
# ==================================================
# Get Maven, necessary for the build
sudo apt-get install git-core maven2
# lucene needs a newer version of java, get it:
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer
# This will bring up an installer, just select OK a couple times
# Get the couchdb-lucene source
git clone git://github.com/rnewson/couchdb-lucene.git
# Now build with maven:
cd couchdb-lucene
mvn
# After the build you should have a subdirectory target, 
# Modify options in the couchdb local.ini file (for me this is /etc/couchdb/local.ini, but it may also be in /usr/local/etc/couchdb/local.ini). Add this at the end (replacing /path/to/couchdb-lucene with the appropriate path):

os_process_timeout=60000 ; increase the timeout from 5 seconds.

[external]
fti=/usr/bin/python /path/to/couchdb-lucene/tools/couchdb-external-hook.py

[httpd_db_handlers]
_fti = {couch_httpd_external, handle_external_req, <<"fti">>}

# Now we have to add a design document to couchdb that hooks up to couchdb-lucene and indexes text. Easiest way is from Futon (at 127.0.0.1:5984/_utils)
# Select the database (store), select "design documents" in the drop down. Create a document and name it "_design/lucene". Add a field "fulltext" to the document, an example to index all document titles:

{
    "by_title": {
        "index": "function(doc) { var ret=new Document(); ret.add(doc.title,
            {'store':'yes'});
            ret.add(doc.journal_id, {'field':'journalID'}); return ret; }"
    },
    "by_journal_id": {
        "index": "function(doc) { var ret=new Document();
            ret.add(doc.journal_id); return ret; }"
    }
}

# Make sure the doc is saved. Might also need to restart the database:
sudo service couchdb restart

# Then run lucene from
/path/to/couchdb/lucene/target/couchdb-lucene*/bin/run

# Then queries can be made like:
http://127.0.0.1:5984/store/_fti/_design/lucene/by_title?q=quantum

== Deploying changes ==

Once you have made and commited changes to your local repository, you
can deploy your changes to the servers using Fabric. It is in requirements.txt so will be available from within your virtualenv.

* Push your local commits to the shared repository
** (akorn) $ fab prepare_deploy
* Pull in commits from shared repository, and restart the server
** (akorn) $ fab deploy