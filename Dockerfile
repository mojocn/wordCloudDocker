FROM python:3.6

ENV TIME_ZONE=${TIME_ZONE}

RUN mkdir /code \
    &&apt-get update \
    &&apt-get -y install freetds-dev \
    &&apt-get -y install unixodbc-dev
COPY code /code
RUN pip install -r /code/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /code

EXPOSE 8111

CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]
