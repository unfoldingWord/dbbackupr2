FROM python:alpine

RUN apk add mariadb mariadb-client mariadb-doc mandoc

WORKDIR /app

COPY requirements.txt .
# ADD https://truststore.pki.rds.amazonaws.com/us-west-2/us-west-2-bundle.pem ./aws-ssl-certs/

# Install requirements
# Disable caching, to keep Docker image lean
RUN pip install --no-cache-dir -r requirements.txt

# Copy in actual backup script
COPY dbbackupr2.py .

CMD [ "python", "/app/dbbackupr2.py" ]
