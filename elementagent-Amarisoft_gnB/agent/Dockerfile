FROM python:3.9
# FROM python:3-slim-buster
# 
WORKDIR /agent

# 
COPY ./requirements.txt /radio_mgmt_agent/requirements.txt

# 
# RUN pip install huawei-lte-api
RUN pip install --no-cache-dir --upgrade -r /radio_mgmt_agent/requirements.txt
RUN apt-get update
RUN apt-get -y install systemd

# ENV PYTHONPATH /agent
# 

COPY ./src  /agent/
#Sanity check
#Create a file in root to make sure
# if the file is created in agent, docker-compose will mount /src and the file will not show
RUN touch /generic.docker