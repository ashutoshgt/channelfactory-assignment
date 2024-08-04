# Use the official Python base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY manage.py .
COPY api/* ./api/
COPY geo/* ./geo/

# Set the DJANGO_SETTINGS_MODULE environment variable for shell
ENV DJANGO_SETTINGS_MODULE=api.settings

# Expose the port that the Django app will run on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
