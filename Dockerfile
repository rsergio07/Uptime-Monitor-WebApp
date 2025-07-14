FROM python:3.9-slim
WORKDIR /app
# Copy requirements.txt directly into the WORKDIR /app
COPY app/requirements.txt .
# Now pip can find it at /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the app/ content into the /app directory
COPY app/ ./app/
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app", "--threads", "2"]