FROM python:3.12.10-slim-bookworm
RUN mkdir -p /app/static /app/templates /app/database /app/database_init /app/scripts
WORKDIR /app
COPY *.py .
COPY ./static/ ./static
COPY ./templates/ ./templates
COPY ./database/*.db ./database_init
COPY requirements.txt .
COPY ./scripts/*.sh  ./scripts
RUN pip install -r requirements.txt
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["/app/scripts/runflask.sh"]
