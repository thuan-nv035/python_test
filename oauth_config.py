import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()
oauth = OAuth()

# Định nghĩa biến google ở đây để các file khác có thể import
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),

    # Sử dụng các Endpoint trực tiếp để tránh lỗi metadata
    authorize_url='https://google.com',
    access_token_url='https://googleapis.com',
    userinfo_endpoint='https://googleapis.com',

    # Các tham số cực kỳ quan trọng
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'  # Ép hiện bảng chọn tài khoản Google
    },

    # Tham số này giúp giải quyết lỗi redirect về google.com
    authorize_params={'access_type': 'offline'},
    server_metadata_url=None
)
