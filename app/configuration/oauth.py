from authlib.integrations.starlette_client import OAuth
from app.configuration.config import settings  

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
google_oauth = oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
    client_auth_method='client_secret_post'
)
