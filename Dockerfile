FROM python:3.9

WORKDIR /app
ADD . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]
