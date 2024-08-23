# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.7-slim

ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install
RUN python -m pip install --upgrade pip
RUN apt update && apt install -y default-libmysqlclient-dev libxslt-dev gcc
COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]