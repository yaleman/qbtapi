FROM python:3.12-slim

#Set the working directory
WORKDIR /usr/src/app

COPY pyproject.toml .

#copy all the files
RUN mkdir qbtapi
COPY qbtapi qbtapi/

RUN python -m pip install .

#Run the command
CMD ["python", "-m", "qbtapi"]