FROM python:3.7
LABEL maintainer="Ivan Smirnov <ivan.smirnov@hpe.com>"

WORKDIR /usr/src/app
COPY app /usr/src/app
RUN pip install -r requirements.txt

EXPOSE 8008/tcp

CMD ["python", "restserver.py"]
