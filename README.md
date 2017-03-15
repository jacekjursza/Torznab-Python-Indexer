# Torznab-Python-Indexer
## A custom indexer for Sonarr

There are currently two providers, tpb and eztv. You can use one or both, depending on your preferred source of content.

### Example install on Ubuntu

This is example how you can install TPI on your private (home) server. The example uses built-in django server which is not reccomended for 'production' purposes. For private use-cases should be fine, though.

Please remember that this is a quick-hack and is not meant for building public services ATM.

$ is a command propmpt.
```
$ git clone https://github.com/jacekjursza/Torznab-Python-Indexer.git
$ cd Torznab-Python-Indexer
$ sudo apt-get build-dep python-lxml
$ virtualenv env
$ source env/bin/activate
$ cd tgw
$ pip install -r requirements.txt
$ python manage.py runserver [domain/IP]:[port]
```

### Testing

To test if the service work, go to:
```
http://[domain]:[port]/tpb/api
```
and check if the service is returning RSS content.
You can also check searching:
```
http://[domain]:[port]/tpb/api?q=Search Phrase
```

### Adding the indexer to Sonarr

1) Go to Sonarr webadmin -> settings -> indexers -> click add -> choose torrent -> torznab -> custom

2) Enable RSS: yes, Enable search: yes.

3) **URL: http://[domain]:[port]/tpb ('/api' is added by Sonarr)**
  * Or **http://[domain]:[port]/eztv** if you want eztv.

4) Categories: 5030,5040

Repeat the above steps again if you want to add both tpb AND eztv.








