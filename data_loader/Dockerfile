# Use Python official image
FROM python:3.11

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all loader scripts into container
COPY . .

# Default command (runs products loader)
CMD ["python", "load_products.py"]
