FROM python:3-alpine

#Set the working directory
WORKDIR /usr/src/app

COPY requirements.txt .

RUN apk add git
RUN python -m pip install -r requirements.txt

#copy all the files
RUN mkdir qbtapi
COPY qbtapi qbtapi/

#Expose the required port
EXPOSE 5000

#Run the command
CMD ["python", "-m", "qbtapi"]