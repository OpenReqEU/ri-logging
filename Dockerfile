FROM python:3-slim

ADD microservice /
ADD tests /

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "./run_docker.py"]
