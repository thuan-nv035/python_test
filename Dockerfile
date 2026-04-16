# Sử dụng Python phiên bản ổn định
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Thiết lập biến môi trường (Flask cần biết file chạy chính)
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Mở cổng 5000 (cổng mặc định của Flask)
EXPOSE 5000

# Lệnh để chạy ứng dụng
CMD ["flask", "run"]
