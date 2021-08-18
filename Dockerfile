FROM ubuntu:bionic

# Update repositories
RUN apt-get update

# Install libraries and tools
RUN apt-get install -y \
    python3-minimal \
    sqlite \
    libsqlite3-dev \
    python3-pip \
    curl
RUN pip3 install -U pip

# Set the working directory to /opp
WORKDIR /opp

# Copy the current directory contents into the container at /app
ADD . /opp

# Install all dependencies
RUN pip3 install -r requirements.txt -r test-requirements.txt

# Allow click to run in UTF mode
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# OpenPassphrase install and setup
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
