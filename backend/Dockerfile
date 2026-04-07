FROM python:3.12-slim

WORKDIR /app

# 빌드 컨텍스트가 루트이므로 backend/ 경로 사용
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
