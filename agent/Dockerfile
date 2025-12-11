FROM python:3.10-slim

WORKDIR /agent

COPY ./requirements.txt /radio_mgmt_agent/requirements.txt
COPY ./src /agent/
COPY ./profiles /agent/profiles

# Install systemd and dependencies
RUN apt-get update \
    && apt-get install -y systemd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade -r /radio_mgmt_agent/requirements.txt

# Expose port
EXPOSE 80

# Command to run the application
CMD ["uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
