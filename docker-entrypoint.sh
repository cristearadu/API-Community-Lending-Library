#!/bin/bash

echo "🚀 Starting the application..."
uvicorn main:app --host 0.0.0.0 --port 8000 