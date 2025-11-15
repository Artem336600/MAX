"""
Простой тестовый сервер для проверки
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/test")
async def test(data: dict):
    return {"received": data}

if __name__ == "__main__":
    print("Starting test server on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
