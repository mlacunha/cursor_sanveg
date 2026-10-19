# Test API Structure

from app.config.settings import get_settings

settings = get_settings()

print("=" * 50)
print("SVEGPA API - Configuration Test")
print("=" * 50)
print(f"App Name: {settings.APP_NAME}")
print(f"Version: {settings.APP_VERSION}")
print(f"Database Host: {settings.DB_HOST}")
print(f"Database Name: {settings.DB_NAME}")
print(f"JWT Algorithm: {settings.ALGORITHM}")
print(f"Token Expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
print("=" * 50)
print("✓ Configuration loaded successfully!")
print("=" * 50)
