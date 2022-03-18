FROM python:3.10-slim

#Set the working directory
WORKDIR /usr/src/app

COPY pyproject.toml .

#copy all the files
RUN mkdir qbtapi
COPY qbtapi qbtapi/

#RUN python -m pip install poetry
#RUN poetry config virtualenvs.create false
#RUN poetry install
RUN python -m pip install .

# RUN python -m pip uninstall -y poetry
#Expose the required port
# EXPOSE 5000

#Run the command
CMD ["python", "-m", "qbtapi"]