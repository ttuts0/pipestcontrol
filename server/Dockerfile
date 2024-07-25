FROM python:3.12-slim-bullseye

RUN apt-get update

RUN mkdir /pestbusterai
RUN mkdir /pestbusterai/detected_pics

WORKDIR /pestbusterai

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

ENV FLASK_APP pestbuster.py

COPY app app
COPY migrations migrations
COPY boot-webapp.sh pestbuster.py config.py ./
RUN chmod +x boot-webapp.sh

EXPOSE 5000
ENTRYPOINT ["./boot-webapp.sh"]


#RUN venv/bin/flask db upgrade
#CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
