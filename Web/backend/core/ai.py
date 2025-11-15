from openai import AsyncOpenAI
from typing import List, Dict, Optional, Any
from .config import settings

class AIEngine:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ):
        """Отправить запрос к DeepSeek API"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        if functions:
            # DeepSeek использует новый формат tools вместо functions
            tools = [
                {
                    "type": "function",
                    "function": func
                }
                for func in functions
            ]
            params["tools"] = tools
            params["tool_choice"] = "auto"
            
            logger.info(f"Sending {len(tools)} tools to DeepSeek")
            logger.info(f"First tool: {tools[0] if tools else 'None'}")
        
        response = await self.client.chat.completions.create(**params)
        return response
    
    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict],
        function_executor: Any,
        max_iterations: int = 3
    ) -> str:
        """Чат с поддержкой function calling"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        for iteration in range(max_iterations):
            logger.info(f"Function calling iteration {iteration + 1}")
            logger.info(f"Sending {len(functions)} functions to AI")
            
            response = await self.chat(messages, functions)
            message = response.choices[0].message
            
            # DeepSeek использует tool_calls вместо function_call
            has_tool_calls = hasattr(message, 'tool_calls') and message.tool_calls
            logger.info(f"AI response has tool_calls: {has_tool_calls}")
            
            # Если ИИ не вызывает функцию - возвращаем ответ
            if not has_tool_calls:
                logger.warning("AI did not call any function")
                return message.content
            
            # Выполняем первый tool call
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            import json
            
            logger.info(f"AI called function: {function_name}")
            logger.info(f"Arguments (raw): {tool_call.function.arguments}")
            
            try:
                function_args = json.loads(tool_call.function.arguments)
                logger.info(f"Arguments (parsed): {function_args}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse arguments: {e}")
                function_args = {}
            
            try:
                result = await function_executor(function_name, function_args)
                logger.info(f"Function result: {result}")
                
                # Добавляем результат в историю (новый формат для tools)
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
    
    def build_system_prompt(self, user_context: Dict) -> str:
        """Создать system prompt с контекстом пользователя (deprecated)"""
        
        prompt = f"""Ты персональный ИИ-ассистент пользователя {user_context.get('name', 'пользователь')}.

Ты помогаешь пользователю управлять его жизнью через модульную систему Eidos.

У пользователя установлены следующие модули:
- Календарь: управление событиями и напоминаниями

Доступные функции:
- create_calendar_event: создать событие в календаре
- get_calendar_events: получить список событий

Отвечай на русском языке, будь дружелюбным и полезным.
Используй эмодзи для улучшения восприятия.
Если пользователь просит создать событие или напоминание - используй функцию create_calendar_event.
"""
        return prompt

# Singleton instance
ai_engine = AIEngine()
