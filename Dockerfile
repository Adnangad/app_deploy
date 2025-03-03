# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (if using Flask)
EXPOSE 5000

# Run the app (change `app.py` to your entry file)
CMD ["python", "app.py"]
