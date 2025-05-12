FROM python:latest 

RUN mkdir ./dashboard

WORKDIR ./dashboard

COPY requirements.txt .

RUN pip install -r ./requirements.txt

COPY financial_dashboard.py .

EXPOSE 8501

CMD streamlit run financial_dashboard.py