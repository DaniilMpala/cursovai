FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR .

ADD ./discountsite .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]