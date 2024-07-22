FROM python:3.11.9

ENV PYTHONUNBUFFERED=1
WORKDIR /backend

# Required to install mysqlclient with Pip
RUN apt-get update \
  && apt-get install python3-dev default-libmysqlclient-dev gcc -y

# Install poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copy poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock* /backend/

# Install application dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the application files into the image
COPY . /backend/

RUN chmod +x docker-entrypoint.sh
# Expose port 5000 on the container
EXPOSE 5000
