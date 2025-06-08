FROM python:3.9-slim

WORKDIR /Activida1Scraping

COPY . .

RUN mkdir -p static/csv static/db

RUN pip install --upgrade pip \
    && pip install -e . \
    && rm -rf /root/.cache/pip

ENV PYTHONPATH="/Activida1Scraping/src"

ENTRYPOINT ["python", "-m"]

CMD ["edu_pad.monitor"]