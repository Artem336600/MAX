"""
HTTP сервер для запуска модулей как отдельных сервисов
"""

from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional, Callable, Dict, Any
import uvicorn
from .module import EidosModule

class ModuleServer:
    """HTTP сервер для модуля"""
    
    def __init__(self, module: EidosModule, host: str = "0.0.0.0", port: int = 8080):
        self.module = module
        self.host = host
        self.port = port
        self.app = FastAPI(title=module.name, version=module.version)
        self._setup_routes()
    
    def _setup_routes(self):
        """Настроить маршруты"""
        
        # Инициализируем хранилище обработчиков
        self._custom_handlers: Dict[str, Callable] = {}
        
        @self.app.post("/{endpoint:path}")
        async def handle_request(
            endpoint: str,
            request: Request,
            x_eidos_module_key: Optional[str] = Header(None)
        ):
            """Обработать запрос от Eidos"""
            
            # Проверить API ключ
            if x_eidos_module_key != self.module.api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")
            
            # Получить данные
            data = await request.json()
            user_id = data.get('user_id')
            user_email = data.get('user_email')
            user_name = data.get('user_name')
            request_data = data.get('data', {})
            
            # Маршрутизация по endpoint
            if endpoint == "message":
                # Обработка сообщения
                message = request_data.get('message', '')
                response = await self.module.on_message(message, user_id)
                return {"response": response}
            
            elif endpoint == "install":
                # Установка модуля
                await self.module.on_install(user_id)
                return {"success": True}
            
            elif endpoint == "uninstall":
                # Удаление модуля
                await self.module.on_uninstall(user_id)
                return {"success": True}
            
            elif endpoint == "enable":
                # Включение модуля
                await self.module.on_enable(user_id)
                return {"success": True}
            
            elif endpoint == "disable":
                # Отключение модуля
                await self.module.on_disable(user_id)
                return {"success": True}
            
            else:
                # Пользовательский endpoint
                handler = self._custom_handlers.get(endpoint)
                if handler:
                    result = await handler(user_id, request_data)
                    return result
                else:
                    raise HTTPException(status_code=404, detail=f"Endpoint not found: {endpoint}")
        
        @self.app.get("/health")
        async def health():
            """Health check"""
            return {
                "status": "healthy",
                "module": self.module.name,
                "version": self.module.version
            }
        
        @self.app.get("/manifest")
        async def manifest():
            """Получить манифест модуля"""
            return self.module.to_manifest()
    
    def add_endpoint(self, path: str, handler: Callable):
        """Добавить пользовательский endpoint"""
        self._custom_handlers[path] = handler
    
    def run(self):
        """Запустить сервер"""
        print(f"🚀 Starting {self.module.name} v{self.module.version}")
        print(f"📡 Listening on http://{self.host}:{self.port}")
        print(f"🔑 API Key: {self.module.api_key[:20]}...")
        print(f"\n✅ Module is ready!")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
