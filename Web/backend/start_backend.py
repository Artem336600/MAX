"""
Запуск backend БЕЗ автоперезагрузки
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # ОТКЛЮЧИТЬ автоперезагрузку
        log_level="info"
    )
