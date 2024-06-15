# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /usr/src/adrift

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat git

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/adrift/entrypoint.sh
RUN chmod +x /usr/src/adrift/entrypoint.sh

# copy project
COPY . .

RUN mkdir -p /usr/src/adrift/logs

# run entrypoint.sh
ENTRYPOINT ["/usr/src/adrift/entrypoint.sh"]