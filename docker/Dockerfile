FROM python:3.12.10-slim-bookworm
RUN mkdir -p /app/static /app/templates /app/database /app/database_init /app/scripts
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt update && apt install dos2unix
COPY *.py .
RUN dos2unix ./*.py
COPY ./scripts/*.sh  ./scripts
RUN dos2unix ./scripts/*.sh
COPY ./static/ ./static
COPY ./templates/ ./templates
COPY ./database/*.db ./database_init
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["/app/scripts/runflask.sh"]
# CMD ["/bin/bash"]
