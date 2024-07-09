FROM python:alpine

WORKDIR /app

COPY dbbackupr2.py .
COPY requirements.txt .
# ADD https://truststore.pki.rds.amazonaws.com/us-west-2/us-west-2-bundle.pem ./aws-ssl-certs/

# Install requirements
# Disable caching, to keep Docker image lean
RUN pip install --no-cache-dir -r requirements.txt

RUN apk add mysql-client

CMD [ "python", "/app/dbbackupr2.py" ]
