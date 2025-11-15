"""
Единый AI движок для всех интерфейсов
"""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional, Callable
import json
import logging

logger = logging.getLogger(__name__)


class UnifiedAIEngine:
    """Единый движок ИИ для Web и MAKS бота"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = "deepseek-chat"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ):
        """Отправить запрос к AI API"""
        
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        if tools:
            # Конвертировать в формат tools
            formatted_tools = [
                {
                    "type": "function",
                    "function": tool
                }
                for tool in tools
            ]
            params["tools"] = formatted_tools
            params["tool_choice"] = "auto"
            
            logger.info(f"Sending {len(formatted_tools)} tools to AI")
        
        response = await self.client.chat.completions.create(**params)
        return response
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        tool_executor: Callable,
        max_iterations: int = 3
    ) -> str:
        """Чат с поддержкой инструментов (function calling)"""
        
        for iteration in range(max_iterations):
            logger.info(f"Tool calling iteration {iteration + 1}")
            
            response = await self.chat(messages, tools)
            message = response.choices[0].message
            
            # Проверить есть ли tool calls
            has_tool_calls = hasattr(message, 'tool_calls') and message.tool_calls
            logger.info(f"AI response has tool_calls: {has_tool_calls}")
            
            if not has_tool_calls:
                # Нет вызовов функций - возвращаем ответ
                return message.content or "Извините, не могу ответить"
            
            # Выполнить tool call
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            
            logger.info(f"AI called function: {function_name}")
            logger.info(f"Arguments: {tool_call.function.arguments}")
            
            try:
                # Парсинг аргументов
                function_args = json.loads(tool_call.function.arguments)
                
                # Выполнение функции
                result = await tool_executor(function_name, function_args)
                logger.info(f"Function result: {result}")
                
                # Добавить результат в историю
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": tool_call.function.arguments
                        }
                    }]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
                
            except Exception as e:
                logger.error(f"Function execution error: {e}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Error: {str(e)}"
                })
        
        # Если достигли лимита итераций
        return "Извините, не удалось выполнить запрос"
    
    async def simple_chat(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Простой чат без инструментов"""
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        response = await self.chat(messages)
        return response.choices[0].message.content or "Извините, не могу ответить"
