from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import secrets

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.module import Module, UserModule

router = APIRouter()

def generate_api_key() -> str:
    """Генерация API ключа для модуля"""
    return f"eidos_module_{secrets.token_urlsafe(32)}"

# Pydantic schemas
class ModuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    manifest: Dict

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    manifest: Optional[Dict] = None
    code: Optional[str] = None
    status: Optional[str] = None

class ModuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    author_id: str
    version: str
    manifest: Dict
    code: Optional[str]
    api_key: Optional[str]
    status: str
    rating: float
    installs: int
    created_at: str
    updated_at: str
    is_installed: bool = False

    class Config:
        from_attributes = True

class UserModuleResponse(BaseModel):
    id: str
    module: ModuleResponse
    enabled: bool
    installed_at: str

@router.post("", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    request: ModuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый модуль"""
    
    module = Module(
        name=request.name,
        description=request.description,
        author_id=current_user.id,
        version=request.version,
        manifest=request.manifest,
        api_key=generate_api_key(),
        status="draft"
    )
    
    db.add(module)
    await db.commit()
    await db.refresh(module)
    
    return ModuleResponse(
        id=module.id,
        name=module.name,
        description=module.description,
        author_id=module.author_id,
        version=module.version,
        manifest=module.manifest,
        code=module.code,
        api_key=module.api_key,
        status=module.status,
        rating=module.rating,
        installs=module.installs,
        created_at=module.created_at.isoformat(),
        updated_at=module.updated_at.isoformat()
    )

@router.get("", response_model=List[ModuleResponse])
async def get_modules(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список модулей"""
    
    query = select(Module)
    
    if status_filter:
        query = query.where(Module.status == status_filter)
    else:
        # По умолчанию показываем только публичные модули
        query = query.where(Module.status == "public")
    
    result = await db.execute(query.order_by(Module.installs.desc()))
    modules = result.scalars().all()
    
    # Проверяем установлены ли модули у пользователя
    installed_result = await db.execute(
        select(UserModule.module_id).where(UserModule.user_id == current_user.id)
    )
    installed_ids = set(row[0] for row in installed_result.all())
    
    return [
        ModuleResponse(
            id=module.id,
            name=module.name,
            description=module.description,
            author_id=module.author_id,
            version=module.version,
            manifest=module.manifest,
            code=None,  # Не показываем код в списке
            api_key=None,  # Не показываем API ключ в списке
            status=module.status,
            rating=module.rating,
            installs=module.installs,
            created_at=module.created_at.isoformat(),
            updated_at=module.updated_at.isoformat(),
            is_installed=module.id in installed_ids
        )
        for module in modules
    ]

@router.get("/my", response_model=List[ModuleResponse])
async def get_my_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить мои созданные модули"""
    
    result = await db.execute(
        select(Module).where(Module.author_id == current_user.id)
    )
    modules = result.scalars().all()
    
    return [
        ModuleResponse(
            id=module.id,
            name=module.name,
            description=module.description,
            author_id=module.author_id,
            version=module.version,
            manifest=module.manifest,
            code=module.code,
            api_key=module.api_key,
            status=module.status,
            rating=module.rating,
            installs=module.installs,
            created_at=module.created_at.isoformat(),
            updated_at=module.updated_at.isoformat()
        )
        for module in modules
    ]

@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить модуль по ID"""
    
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Проверяем установлен ли модуль
    installed_result = await db.execute(
        select(UserModule).where(
            and_(
                UserModule.user_id == current_user.id,
                UserModule.module_id == module_id
            )
        )
    )
    is_installed = installed_result.scalar_one_or_none() is not None
    
    # Показываем API ключ только автору
    show_api_key = module.author_id == current_user.id
    
    return ModuleResponse(
        id=module.id,
        name=module.name,
        description=module.description,
        author_id=module.author_id,
        version=module.version,
        manifest=module.manifest,
        code=module.code if show_api_key else None,
        api_key=module.api_key if show_api_key else None,
        status=module.status,
        rating=module.rating,
        installs=module.installs,
        created_at=module.created_at.isoformat(),
        updated_at=module.updated_at.isoformat(),
        is_installed=is_installed
    )

@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    request: ModuleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить модуль"""
    
    result = await db.execute(
        select(Module).where(
            and_(
                Module.id == module_id,
                Module.author_id == current_user.id
            )
        )
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or you don't have permission"
        )
    
    # Update fields
    if request.name is not None:
        module.name = request.name
    if request.description is not None:
        module.description = request.description
    if request.version is not None:
        module.version = request.version
    if request.manifest is not None:
        module.manifest = request.manifest
    if request.code is not None:
        module.code = request.code
    if request.status is not None:
        module.status = request.status
    
    module.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(module)
    
    return ModuleResponse(
        id=module.id,
        name=module.name,
        description=module.description,
        author_id=module.author_id,
        version=module.version,
        manifest=module.manifest,
        code=module.code,
        api_key=module.api_key,
        status=module.status,
        rating=module.rating,
        installs=module.installs,
        created_at=module.created_at.isoformat(),
        updated_at=module.updated_at.isoformat()
    )

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить модуль (только автор)"""
    
    result = await db.execute(
        select(Module).where(
            and_(
                Module.id == module_id,
                Module.author_id == current_user.id
            )
        )
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or you don't have permission"
        )
    
    # Удалить все установки модуля
    user_modules_result = await db.execute(
        select(UserModule).where(UserModule.module_id == module_id)
    )
    user_modules = user_modules_result.scalars().all()
    for um in user_modules:
        await db.delete(um)
    
    # Удалить модуль
    await db.delete(module)
    await db.commit()

@router.post("/{module_id}/install", status_code=status.HTTP_201_CREATED)
async def install_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Установить модуль"""
    
    # Проверяем существование модуля
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Проверяем не установлен ли уже
    existing = await db.execute(
        select(UserModule).where(
            and_(
                UserModule.user_id == current_user.id,
                UserModule.module_id == module_id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module already installed"
        )
    
    # Устанавливаем модуль
    user_module = UserModule(
        user_id=current_user.id,
        module_id=module_id
    )
    
    db.add(user_module)
    
    # Увеличиваем счётчик установок
    module.installs += 1
    
    await db.commit()
    
    return {"message": "Module installed successfully"}

@router.delete("/{module_id}/uninstall", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить модуль"""
    
    result = await db.execute(
        select(UserModule).where(
            and_(
                UserModule.user_id == current_user.id,
                UserModule.module_id == module_id
            )
        )
    )
    user_module = result.scalar_one_or_none()
    
    if not user_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not installed"
        )
    
    await db.delete(user_module)
    
    # Уменьшаем счётчик установок
    module_result = await db.execute(select(Module).where(Module.id == module_id))
    module = module_result.scalar_one_or_none()
    if module and module.installs > 0:
        module.installs -= 1
    
    await db.commit()

@router.get("/installed/list", response_model=List[UserModuleResponse])
async def get_installed_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить установленные модули пользователя"""
    
    result = await db.execute(
        select(UserModule, Module).join(Module).where(UserModule.user_id == current_user.id)
    )
    
    user_modules = []
    for user_module, module in result.all():
        user_modules.append(UserModuleResponse(
            id=user_module.id,
            module=ModuleResponse(
                id=module.id,
                name=module.name,
                description=module.description,
                author_id=module.author_id,
                version=module.version,
                manifest=module.manifest,
                code=None,
                api_key=None,
                status=module.status,
                rating=module.rating,
                installs=module.installs,
                created_at=module.created_at.isoformat(),
                updated_at=module.updated_at.isoformat(),
                is_installed=True
            ),
            enabled=user_module.enabled,
            installed_at=user_module.installed_at.isoformat()
        ))
    
    return user_modules
