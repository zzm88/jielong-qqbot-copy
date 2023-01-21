FROM python:3.9
COPY ./app /app
WORKDIR /app
RUN pip3 install -r requirements2.txt -i https://mirrors.aliyun.com/pypi/simple/
CMD ["python","/app/bot.py"]
