FROM python:3.9-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src
COPY test test

RUN python -m unittest discover -v test

CMD ["python", "src/main.py"]