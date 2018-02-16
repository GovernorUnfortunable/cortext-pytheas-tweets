# Base image.

FROM python:3.5

# Set the DEBIAN_FRONTEND environment variable only during the build
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install nano -y

# copy scripts
RUN mkdir /opt/pytheas_tweets
COPY . /opt/pytheas_tweets

#prepare work directory
WORKDIR /opt/pytheas_tweets

# install flask & co
RUN pip install -r requirements.txt

# install modified twitterscrape package
COPY ./twitterscraper /opt/pytheas_tweets/twitterscraper
RUN cd ./twitterscraper/ && python setup.py install

# prepare port
EXPOSE 5000

# Define working volumes
VOLUME ["/opt/pytheas_tweets/conf"]

#lauch app
CMD python app.py
