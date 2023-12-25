FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "carol_of_the_screens", "wizard_in_winter.mp3", "wizard_in_winter.csv"]