# Torznab-Python-Indexer

example install on Ubuntu:



git clone https://github.com/jacekjursza/Torznab-Python-Indexer.git
cd Torznab-Python-Indexer
sudo apt-get build-dep python-lxml
virtualenv env
source env/bin/activate
cd tgw
pip install -r requirements.txt
python manage.py runserver [domain/IP]:[port]