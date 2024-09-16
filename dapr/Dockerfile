# Use the official Python image from the Docker Hub
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container
COPY requirements.txt ./requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code into the container
COPY publisher/ ./publisher/
COPY subscriber/ ./subscriber/
COPY dapr.yaml ./dapr.yaml
COPY components/ /root/.dapr/components/
COPY tursodb.py ./tursodb.py
COPY .env ./.env

# Install Dapr CLI
RUN apt-get update && apt-get install -y wget \
    && wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash \
    && dapr init --slim \
    && rm -rf /var/lib/apt/lists/*
    

# Expose the ports the apps run on
EXPOSE 8000
EXPOSE 8001
EXPOSE 3500
EXPOSE 3501

# Command to run the Dapr services
CMD ["dapr", "run", "-f", "./dapr.yaml"]