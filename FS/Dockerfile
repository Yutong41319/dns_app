FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fs.py .
EXPOSE 9090
CMD ["python", "fs.py"]
