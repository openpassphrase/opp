FROM ubuntu:xenial

# Init
RUN apt-get update

# Install python3.7, pip and other dependencies
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7 
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 0
RUN apt-get install -y sqlite python3-pip
RUN pip3 install -U pip

# Allow click to run in UTF mode
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# OpenPassphrase install and setup
WORKDIR /opp
ADD . /opp
RUN pip install -r requirements.txt -r test-requirements.txt
RUN python3 setup.py install
RUN mkdir /etc/opp
RUN echo '[DEFAULT]' > /etc/opp/opp.cfg
RUN echo 'db_connect = sqlite://///root/opp.sqlite' >> /etc/opp/opp.cfg
RUN opp-db init
RUN opp-db add-user -u demo -p demo --phrase=phrase

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Configure server for Docker
RUN sed -i "s/localhost/0.0.0.0/" opp/flask/__init__.py

# Start server
CMD python3 opp/flask/__init__.py
