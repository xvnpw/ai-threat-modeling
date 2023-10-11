# Container image that runs your code
FROM python@sha256:88880bc85b0e3342ff416c796df7ad9079b2805f92a6ebfc5c84ac582fb25de9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY templates ./templates

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
