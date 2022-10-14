FROM python:3.11.0rc2-slim

WORKDIR /mydir

COPY . .

RUN pip install -r requirements.txt

CMD ["python","-m","flask","run","--host=0.0.0.0"]