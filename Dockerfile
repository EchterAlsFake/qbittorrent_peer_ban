FROM python:3-alpine
RUN mkdir /app
COPY ./main.py /app
COPY ./requirements.txt /app
COPY ./docker-config.ini /app/config.ini
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-u", "main.py", "v2", "--start"]