FROM python:3-slim

WORKDIR /container

COPY . /container

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV NAME RiLogging

CMD ["python", "run.py", "configuration.json", "true"]