FROM python:3.12.10-slim-bookworm
RUN mkdir -p /app/static /app/templates /app/database
WORKDIR /app
COPY ./app.py ./
COPY ./helpers.py ./
COPY ./requirements.txt ./
COPY ./static/ ./static
COPY ./templates/ ./templates
COPY ./database/ ./database
RUN pip install -r requirements.txt
CMD ["/bin/bash"]
