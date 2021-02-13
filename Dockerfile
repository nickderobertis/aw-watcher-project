FROM python:3.6

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y qt5-default

RUN pip install dist/aw-watcher-project-0.1.0.tar.gz
