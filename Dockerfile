FROM python:3-slim

ADD microservice /
ADD tests /

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

#RUN pytest --cov=./microservice --cov-report=xml --cov-config=.coveragerc test_all.py

CMD [ "python", "./run_docker.py"]