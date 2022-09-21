# start by pulling the python image
FROM python:3.9-slim

RUN apt update && apt install -y \
    vim \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# copy every content from the local file to the image
COPY . /app

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

EXPOSE 8080
# run
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "manage:app"]
