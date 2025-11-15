from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.module_page import ModulePage
from models.module import Module, UserModule

router = APIRouter()

class ModulePageResponse(BaseModel):
    id: str
    module_id: str
    module_name: str
    title: str
    icon: Optional[str]
    path: str
    component_url: Optional[str]
    order: int
    enabled: bool

    class Config:
        from_attributes = True

@router.get("", response_model=List[ModulePageResponse])
async def get_user_module_pages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить страницы модулей для пользователя (для sidebar)"""
    
    pages = []
    
    # 1. Получить черновики пользователя (для тестирования)
    draft_modules_result = await db.execute(
        select(Module)
        .where(
            and_(
                Module.author_id == current_user.id,
                Module.status == 'draft'
            )
        )
    )
    draft_modules = draft_modules_result.scalars().all()
    
    # Добавить страницы из черновиков
    for module in draft_modules:
        manifest = module.manifest or {}
        pages_config = manifest.get('pages', [])
        print(f"[DEBUG] Draft module: {module.name}, manifest: {manifest}")  # Debug
        for page_config in pages_config:
            print(f"[DEBUG] Adding draft page: {page_config}")  # Debug
            pages.append(ModulePageResponse(
                id=f"draft-{module.id}",
                module_id=module.id,
                module_name=module.name,
                title=page_config.get('title', module.name),
                icon=page_config.get('icon'),
                path=page_config.get('path', f'/dashboard/{module.name.lower()}'),
                component_url=page_config.get('component_url'),
                order=page_config.get('order', 100),
                enabled=True
            ))
    
    # 2. Получить установленные и активные модули пользователя
    user_modules_result = await db.execute(
        select(UserModule.module_id)
        .where(
            and_(
                UserModule.user_id == current_user.id,
                UserModule.enabled == True
            )
        )
    )
    user_module_ids = [row[0] for row in user_modules_result.all()]
    
    # Получить страницы этих модулей
    if user_module_ids:
        pages_result = await db.execute(
            select(ModulePage, Module.name)
            .join(Module, ModulePage.module_id == Module.id)
            .where(
                and_(
                    ModulePage.module_id.in_(user_module_ids),
                    ModulePage.enabled == True
                )
            )
            .order_by(ModulePage.order)
        )
        
        for page, module_name in pages_result.all():
            pages.append(ModulePageResponse(
                id=page.id,
                module_id=page.module_id,
                module_name=module_name,
                title=page.title,
                icon=page.icon,
                path=page.path,
                component_url=page.component_url,
                order=page.order,
                enabled=page.enabled
            ))
    
    # 3. Добавить встроенные модули
    builtin = await get_builtin_pages()
    pages.extend(builtin)
    
    # Сортировать по order
    pages.sort(key=lambda x: x.order)
    
    return pages

async def get_builtin_pages() -> List[ModulePageResponse]:
    """Получить встроенные страницы модулей"""
    
    return [
        ModulePageResponse(
            id="builtin-sleep",
            module_id="sleep_tracker",
            module_name="Sleep Tracker",
            title="Сон",
            icon="😴",
            path="/dashboard/sleep",
            component_url=None,
            order=10,
            enabled=True
        ),
        ModulePageResponse(
            id="builtin-habits",
            module_id="habit_tracker",
            module_name="Habit Tracker",
            title="Привычки",
            icon="💪",
            path="/dashboard/habits",
            component_url=None,
            order=11,
            enabled=True
        ),
        ModulePageResponse(
            id="builtin-finance",
            module_id="finance_manager",
            module_name="Finance Manager",
            title="Финансы",
            icon="💰",
            path="/dashboard/finance",
            component_url=None,
            order=12,
            enabled=True
        )
    ]

@router.get("/all", response_model=List[ModulePageResponse])
async def get_all_module_pages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить все доступные страницы модулей (для настроек)"""
    
    pages_result = await db.execute(
        select(ModulePage, Module.name)
        .join(Module, ModulePage.module_id == Module.id)
        .order_by(ModulePage.order)
    )
    
    pages = []
    for page, module_name in pages_result.all():
        pages.append(ModulePageResponse(
            id=page.id,
            module_id=page.module_id,
            module_name=module_name,
            title=page.title,
            icon=page.icon,
            path=page.path,
            component_url=page.component_url,
            order=page.order,
            enabled=page.enabled
        ))
    
    # Добавить встроенные
    builtin = await get_builtin_pages()
    pages.extend(builtin)
    
    pages.sort(key=lambda x: x.order)
    
    return pages
