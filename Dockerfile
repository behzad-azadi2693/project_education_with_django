FROM python

WORKDIR /code

COPY . /code/

RUN pip install -U pip

RUN pip install -r requirements.txt

EXPOSE 8000
