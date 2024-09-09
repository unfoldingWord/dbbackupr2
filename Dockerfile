FROM python:alpine

# Manually compile MySQL 8.4.2 Community, to properly deal with GENERATED columns
RUN apk add --no-cache bash build-base autoconf openssl openssl-dev ncurses ncurses-dev wget cmake && \
    wget -O /tmp/mysql-8.4.2.tar.gz https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.2.tar.gz && \
    cd /tmp && tar -xf /tmp/mysql-8.4.2.tar.gz && \
    cd /tmp/mysql-8.4.2 && mkdir build && cd build/ && \
    cmake .. -DWITHOUT_SERVER:BOOL=ON -DCMAKE_INSTALL_PREFIX=/ && make && make install && \
    rm -rf /tmp/mysql* && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .
# ADD https://truststore.pki.rds.amazonaws.com/us-west-2/us-west-2-bundle.pem ./aws-ssl-certs/

# Install requirements
# Disable caching, to keep Docker image lean
RUN pip install --no-cache-dir -r requirements.txt

# Copy in actual backup script
COPY dbbackupr2.py .

CMD [ "python", "/app/dbbackupr2.py" ]
