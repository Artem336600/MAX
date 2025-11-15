from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db
from api.maks_auth import router as maks_auth_router
from api.calendar import router as calendar_router
from api.modules import router as modules_router
from api.module_proxy import router as module_proxy_router
from api.notifications import router as notifications_router
from api.widgets import router as widgets_router
from api.sleep_tracker import router as sleep_tracker_router
from api.habit_tracker import router as habit_tracker_router
from api.finance_manager import router as finance_manager_router
from api.module_pages import router as module_pages_router
from api.schedule_optimizer import router as schedule_optimizer_router

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Eidos API",
    version="0.1.0"
)

# CORS - ДОЛЖЕН БЫТЬ ПЕРВЫМ!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Eidos Backend...")
    await init_db()
    logger.info("Database initialized - Backend ready!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Eidos Backend...")

# Include routers - только MAKS авторизация и модули
app.include_router(maks_auth_router)  # MAKS авторизация
app.include_router(calendar_router, prefix="/api/v1/calendar/events", tags=["calendar"])
app.include_router(modules_router, prefix="/api/v1/modules", tags=["modules"])
app.include_router(module_proxy_router, prefix="/api/v1/modules", tags=["module-proxy"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(widgets_router, prefix="/api/v1/widgets", tags=["widgets"])
app.include_router(sleep_tracker_router, prefix="/api/v1/sleep", tags=["sleep-tracker"])
app.include_router(habit_tracker_router, prefix="/api/v1/habits", tags=["habit-tracker"])
app.include_router(finance_manager_router, prefix="/api/v1/finance", tags=["finance-manager"])
app.include_router(module_pages_router, prefix="/api/v1/module-pages", tags=["module-pages"])
app.include_router(schedule_optimizer_router, prefix="/api/v1/schedule", tags=["schedule-optimizer"])

@app.get("/")
async def root():
    return {"message": "Eidos API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
