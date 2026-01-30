FROM python:3
ENV TZ="Asia/Ho_Chi_Minh"
WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /usr/src/app/
COPY .env /usr/src/app/
CMD [ "python", "./apidiscover.py" ]
