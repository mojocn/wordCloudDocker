FROM python:3.6

ENV TIME_ZONE=${TIME_ZONE} \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome

COPY sources.list /etc/apt/china.sources.list

RUN mkdir /code \
    &&mv /etc/apt/sources.list /etc/apt/source.list.bak \
    &&mv /etc/apt/china.sources.list /etc/apt/sources.list\
    &&apt-get update \
    &&apt-get -y install freetds-dev  \
    &&apt-get -y install unixodbc-dev

RUN apt-get update \
    &&apt-get -y install xfonts-wqy ttf-wqy-microhei

# Install Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# Install Google Chrome
# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

COPY code /code
RUN pip install -r /code/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
WORKDIR /code

EXPOSE 8111

CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]
