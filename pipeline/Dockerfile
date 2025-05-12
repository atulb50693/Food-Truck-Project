
FROM python:latest 

RUN mkdir pipeline

WORKDIR ./pipeline

RUN mkdir data-files

RUN mkdir logs

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY data-files ./data-files

COPY transform.py .

COPY load.py .

COPY extract.py .

COPY pipeline.py .

EXPOSE 3306

CMD python3 pipeline.py