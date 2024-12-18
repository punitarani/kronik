"""
kronik/be/server.py

Usage: poetry run uvicorn kronik.be.server:app --port 8000 [--reload]
"""

from time import time

import psutil
from fastapi import FastAPI

app = FastAPI(title="kronik-api")


def uptime() -> float:
    return time() - psutil.boot_time()


@app.get("/")
async def status():
    return {
        "status": "healthy",
        "time": time(),
        "uptime": uptime(),
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
    }
