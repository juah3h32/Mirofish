"""
LLM客户端封装
使用 Anthropic Claude API
"""

import json
import re
from typing import Optional, Dict, Any, List
from anthropic import Anthropic

from ..config import Config


class LLMClient:
    """LLM客户端 - Anthropic Claude API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")

        # The Anthropic SDK appends /v1/<endpoint> to the base_url.
        # If the configured URL already ends with /v1, strip it to avoid /v1/v1/messages → 404.
        raw_base = base_url or Config.LLM_BASE_URL or ''
        if raw_base.endswith('/v1') or raw_base.endswith('/v1/'):
            raw_base = raw_base.rstrip('/').removesuffix('/v1')
        # Only pass base_url if it differs from Anthropic's default
        kwargs = {"api_key": self.api_key}
        if raw_base and raw_base != 'https://api.anthropic.com':
            kwargs["base_url"] = raw_base
        self.client = Anthropic(**kwargs)

    def _split_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Separa system message del resto. Retorna (system_text, chat_messages)."""
        system_parts = []
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system_parts.append(m["content"])
            else:
                chat_messages.append({"role": m["role"], "content": m["content"]})
        system_text = "\n\n".join(system_parts) if system_parts else None
        return system_text, chat_messages

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）

        Returns:
            模型响应文本
        """
        system_text, chat_messages = self._split_messages(messages)

        if response_format and response_format.get("type") == "json_object":
            json_instruction = "\nYou must respond with valid JSON only. Do not include any other text, markdown fences, or explanations."
            system_text = (system_text or "") + json_instruction

        kwargs = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_text:
            kwargs["system"] = system_text

        response = self.client.messages.create(**kwargs)

        # Extraer texto de la respuesta
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        # Limpiar <think> tags si existen
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        # Limpiar markdown code blocks
        content = re.sub(r'^```(?:json)?\s*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\n?```\s*$', '', content)
        return content.strip()

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Intentar extraer JSON de la respuesta si hay texto alrededor
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"LLM返回的JSON格式无效: {response[:500]}")
