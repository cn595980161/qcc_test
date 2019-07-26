FROM xvfb-python3

WORKDIR /usr/src/app

RUN apt-get install -y libatk-bridge2.0-0
RUN apt-get install -y 	libgtk-3-0
RUN apt-get install -y dbus
RUN service dbus start
RUN service cron start

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

CMD ["python3", "run.py"]