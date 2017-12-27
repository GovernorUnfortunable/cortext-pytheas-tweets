# Pytheas_tweet
Simple web interface to download tweets without the use of API (only historical HTML flux from twitter.com/search)

## based on :
- twitterscrap
- flask
- request
- bs4

## next to do : 
* processing db 
* documentation
* parse more filters

## how to use ? 
### with docker and docker-compose

1. first git clone this repo
``` 
git clone --recursive https://github.com/cortext/simple-tweet-web-extract.git
```

2. run docker
```
docker build -t cortext/cortext_pytheas . && docker-compose up 
```


### with virtualenv and python 

1. Locally you can also more easily (and to debug principaly) directly create a virtualenv with python 3.x
```
virtualenv env3 -p /usr/bin/python3 && source ./env3/bin/activate
```

2. Then install dependancies :
``` 
pip install -r requirements.txt
git clone https://github.com/ikario404/twitterscraper.git
cd twitterscraper && python setup.py install && cd ..
```

3. Finally :
``` 
python app.py
```
