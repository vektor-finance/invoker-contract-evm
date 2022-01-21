# Based on https://github.com/eth-brownie/brownie/blob/master/Dockerfile
FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install linux dependencies
RUN apt-get update && apt-get install -y wait-for-it libssl-dev npm

RUN npm install -g ganache-cli

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r /app/requirements.txt

# Compile code
COPY . /app
RUN brownie compile

# Create empty .env
RUN touch .env

EXPOSE 8545

CMD [ "brownie", "console" ]
