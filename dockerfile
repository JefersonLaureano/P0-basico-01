FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 80

CMD ["streamlit", "run", "src/web.py", "--server.port=80", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]