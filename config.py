class Settings:
    def __init__(self):
        self.SECRET_KEY = "your-super-secret-test-key"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()
