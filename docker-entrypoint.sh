#!/bin/bash

# Wait for database to be ready
alembic upgrade head

# Create admin user if it doesn't exist
python << END
from models.user import User
from services.auth import get_password_hash
from database import SessionLocal, engine
import os

db = SessionLocal()
admin = db.query(User).filter(User.username == os.getenv('ADMIN_USERNAME')).first()

if not admin:
    admin = User(
        username=os.getenv('ADMIN_USERNAME'),
        email=os.getenv('ADMIN_EMAIL'),
        password=get_password_hash(os.getenv('ADMIN_PASSWORD')),
        role='admin'
    )
    db.add(admin)
    db.commit()
    print("Admin user created successfully")
else:
    print("Admin user already exists")

db.close()
END

# Execute the CMD
exec "$@" 