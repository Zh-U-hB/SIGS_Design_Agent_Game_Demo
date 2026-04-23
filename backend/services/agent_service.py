# agent_service.py — AI Agent 业务逻辑
# 职责：调用 LLM API 处理用户创意输入，生成专业设计说明

import httpx
from typing import Dict

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def translate_to_design_spec(emotion_tags: Dict, user_input: str, location_label: str) -> str:
    """
    调用 LLM API 将用户创意翻译为专业设计说明
    
    Args:
        emotion_tags: 用户选择的情绪标签
        user_input: 用户的文字描述
        location_label: 用户选择的位置标签
    
    Returns:
        设计说明文本
    """
    if not settings.LLM_API_KEY or not settings.LLM_API_URL:
        logger.warning("LLM API 配置不完整，返回占位响应")
        return _generate_fallback_design_spec(emotion_tags, user_input, location_label)
    
    prompt = _build_prompt(emotion_tags, user_input, location_label)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": settings.LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的校园景观设计AI助手。根据用户的情绪标签、文字描述和选择的位置，生成简洁专业的设计说明（50-100字）。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = await client.post(settings.LLM_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            design_spec = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            logger.info(f"LLM 调用成功，生成设计说明: {design_spec[:50]}...")
            return design_spec
            
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API 调用失败: {e.response.status_code} - {e.response.text}")
        return _generate_fallback_design_spec(emotion_tags, user_input, location_label)
    except Exception as e:
        logger.error(f"LLM API 调用异常: {e}")
        return _generate_fallback_design_spec(emotion_tags, user_input, location_label)


def _build_prompt(emotion_tags: Dict, user_input: str, location_label: str) -> str:
    """
    构建 LLM 提示词
    
    Args:
        emotion_tags: 用户选择的情绪标签
        user_input: 用户的文字描述
        location_label: 用户选择的位置标签
    
    Returns:
        完整的提示词字符串
    """
    emotion_desc = ", ".join(emotion_tags.keys()) if emotion_tags else "无特定情绪"
    
    prompt = f"""
情绪标签: {emotion_desc}
位置: {location_label}
用户描述: {user_input if user_input else "无文字描述"}

基于以上信息，生成一个专业的设计说明，用于指导后续的景观设计或建筑装饰设计。
要求：
1. 简洁明了（50-100字）
2. 专业术语准确
3. 体现校园特色
4. 适合实际施工
"""
    return prompt.strip()


def _generate_fallback_design_spec(emotion_tags: Dict, user_input: str, location_label: str) -> str:
    """
    当 LLM API 调用失败时生成占位设计说明
    
    Args:
        emotion_tags: 用户选择的情绪标签
        user_input: 用户的文字描述
        location_label: 用户选择的位置标签
    
    Returns:
        占位设计说明
    """
    emotion_desc = ", ".join(emotion_tags.keys()) if emotion_tags else "宁静"
    
    fallback_spec = f"基于{emotion_desc}的氛围和{location_label}的校园位置"
    
    if user_input:
        fallback_spec += f"，结合{user_input}的设计理念"
    
    fallback_spec += "，打造适合学习和交流的校园空间。"
    
    logger.warning(f"使用占位设计说明: {fallback_spec}")
    return fallback_spec
