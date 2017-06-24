FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    sqlite \
    libsqlite3-dev \
    python3.5-dev \
    python-pip \
    curl

RUN pip install -U pip

# Set the working directory to /opp
WORKDIR /opp

# Copy the current directory contents into the container at /app
ADD . /opp

RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
RUN python setup.py install
RUN mkdir /etc/opp
RUN echo '[DEFAULT]' > /etc/opp/opp.cfg
RUN echo 'db_connect = sqlite://///root/opp.sqlite' >> /etc/opp/opp.cfg
RUN opp-db init
RUN opp-db add-user -u demo -p demo --phrase=phrase

# Make port 5000 available to the world outside this container
EXPOSE 5000
CMD python opp/flask/__init__.py
