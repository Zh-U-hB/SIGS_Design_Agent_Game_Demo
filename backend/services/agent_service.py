# agent_service.py — AI Agent 业务逻辑
# 职责：调用 LLM API 处理用户创意输入，生成专业设计说明

import httpx

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def translate_to_design_spec(emotion_tags: list[str] | None, user_input: str, location_label: str | None) -> dict:
    """调用 LLM API 将用户创意翻译为专业设计说明，返回 ai_response 和 design_description"""
    if not settings.LLM_API_KEY or not settings.LLM_API_URL:
        logger.warning("LLM API 配置不完整，返回占位响应")
        return _generate_fallback_result(emotion_tags, user_input, location_label)

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
                        "content": (
                    "你是一个专业的校园景观设计AI助手。"
                    "根据用户的情绪标签、文字描述和选择的位置，"
                    "生成简洁专业的设计说明（50-100字）。"
                )
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
            return {
                "ai_response": design_spec,
                "design_description": design_spec,
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API 调用失败: {e.response.status_code} - {e.response.text}")
        return _generate_fallback_result(emotion_tags, user_input, location_label)
    except Exception as e:
        logger.error(f"LLM API 调用异常: {e}")
        return _generate_fallback_result(emotion_tags, user_input, location_label)


def _build_prompt(emotion_tags: list[str] | None, user_input: str, location_label: str | None) -> str:
    """构建 LLM 提示词"""
    emotion_desc = ", ".join(emotion_tags) if emotion_tags else "无特定情绪"

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


def _generate_fallback_result(emotion_tags: list[str] | None, user_input: str, location_label: str | None) -> dict:
    """当 LLM API 调用失败时生成占位 ai_response 和 design_description"""
    emotion_desc = ", ".join(emotion_tags) if emotion_tags else "宁静"

    ai_response = f"感谢你分享了关于{location_label}的想法"
    if user_input:
        ai_response += f"：「{user_input[:50]}」"
    ai_response += "。我已理解你的需求，正在为你构思设计方案。"

    design_description = f"基于{emotion_desc}的氛围"
    if location_label:
        design_description += f"和{location_label}的校园位置"
    if user_input:
        design_description += f"，结合「{user_input[:30]}」的设计理念"
    design_description += "，打造适合学习和交流的校园空间。"

    logger.warning(f"使用占位响应 — ai_response: {ai_response[:40]}...")
    return {
        "ai_response": ai_response,
        "design_description": design_description,
    }
