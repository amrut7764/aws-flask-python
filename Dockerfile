FROM python:2.7.15-alpine3.8


COPY requirements.txt .
RUN pip install -r requirements.txt && mkdir /src
WORKDIR /src
COPY . .
EXPOSE 5000
ENTRYPOINT [ "python", "/src/app.py" ]