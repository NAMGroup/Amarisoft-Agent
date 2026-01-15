FROM python:3.9
# FROM python:3-slim-buster
# 
WORKDIR /agent

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    systemd \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

# 
COPY ./requirements.txt /radio_mgmt_agent/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /radio_mgmt_agent/requirements.txt

# 
# RUN pip install huawei-lte-api
# ENV PYTHONPATH /agent
# 

COPY ./src  /agent/
#Sanity check
#Create a file in root to make sure
# if the file is created in agent, docker-compose will mount /src and the file will not show
RUN touch /gNodeB_service.docker

CMD ["uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]