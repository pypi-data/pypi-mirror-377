from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from .bot import Bot


class BaseEvent(BaseModel):
    user_id: int
    peer_id: int
    payload: Optional[Dict[str, Any]] = None
    bot: Optional["Bot"] = Field(None, exclude=True)

    class Config:
        extra = "allow"
        populate_by_name = True
        arbitrary_types_allowed = True


class Message(BaseEvent):
    user_id: int = Field(..., alias="from_id")
    text: str
    conversation_message_id: Optional[int] = None

    async def answer(
            self, text: str, keyboard: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Упрощенная отправка сообщения в ответ на текущее.
        Автоматически использует peer_id из события.
        """
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to the event.")
        return await self.bot.send_message(
            peer_id=self.peer_id, text=text, keyboard=keyboard, **kwargs
        )

    @model_validator(mode="before")
    @classmethod
    def process_raw_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает вложенный объект 'message' и парсит его 'payload'.
        Это решает все проблемы с порядком валидаторов.
        """
        # Шаг 1: Извлекаем вложенный объект `message`
        if "message" in data and isinstance(data["message"], dict):
            processed_data = data["message"]
            if "client_info" in data:
                processed_data["client_info"] = data["client_info"]
        else:
            processed_data = data

        # Шаг 2: Парсим payload внутри извлеченного объекта
        payload_str = processed_data.get("payload")
        if payload_str and isinstance(payload_str, str):
            try:
                processed_data["payload"] = json.loads(payload_str)
            except json.JSONDecodeError:
                processed_data["payload"] = {}

        return processed_data


class Callback(BaseEvent):
    event_id: str
    conversation_message_id: int

    async def edit_text(self, text: str, keyboard: Optional[str] = None, **kwargs: Any):
        """
        Упрощенное редактирование сообщения в ответ на callback.
        Автоматически убирает "часики" и редактирует сообщение.
        """
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to the event.")

        _, response = await asyncio.gather(
            self.bot.answer_callback(self),
            self.bot.edit_message(
                peer_id=self.peer_id,
                conversation_message_id=self.conversation_message_id,
                text=text,
                keyboard=keyboard,
                **kwargs,
            ),
        )
        return response

    async def answer_and_send(self, text: str, keyboard: Optional[str] = None, **kwargs: Any):
        """
        Отвечает на callback (убирает "часики") и отправляет НОВОЕ сообщение.
        """
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to the event.")

        _, response = await asyncio.gather(
            self.bot.answer_callback(self),
            self.bot.send_message(
                peer_id=self.peer_id, text=text, keyboard=keyboard, **kwargs
            )
        )
        return response

    @model_validator(mode="before")
    @classmethod
    def parse_payload_from_str(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        payload_str = data.get("payload")
        if payload_str and isinstance(payload_str, str):
            data["payload"] = json.loads(payload_str)
        return data


class VKUser(BaseModel):
    """Модель для данных пользователя, получаемых через users.get."""

    id: int
    first_name: str
    last_name: str
    bdate: Optional[str] = None
    sex: Optional[int] = None


VKEvent = Union[Message, Callback]
