FROM python:3-alpine
# An argument needed to be passed
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

# Set needed settings
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}

# Test for secret key
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Load data

# Run this command in docker terminal
# python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json

# Copy the rest of the application files
COPY . .

# Copy the entrypoint.sh script
COPY entrypoint.sh ./entrypoint.sh

# Make the entrypoint.sh executable

COPY . .
RUN chmod +x ./entrypoint.sh

EXPOSE 8000
# Run the server
CMD [ "./entrypoint.sh" ]