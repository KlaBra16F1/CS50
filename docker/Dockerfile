FROM python:3.12.10-slim-bookworm
RUN mkdir -p /app/static /app/templates /app/database
WORKDIR /app
COPY *.py .
COPY ./static/ ./static
COPY ./templates/ ./templates
COPY ./database/ ./database_init
COPY requirements.txt runflask.sh entrypoint.sh .
RUN pip install -r requirements.txt
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/runflask.sh"]
