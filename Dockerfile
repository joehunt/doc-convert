FROM python:3.13-slim AS build

# Install pandoc and wkhtmltopdf
RUN apt-get update && apt-get install -y pandoc wkhtmltopdf \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]