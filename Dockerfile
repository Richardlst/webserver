FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Expose port cho ứng dụng Flask
EXPOSE 5000

# Chạy ứng dụng với gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]