# image_service.py — 图片生成业务逻辑
# 职责：调用图片生成 API（如Stable Diffusion），处理异步生成任务

import httpx
from typing import Dict, Optional

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def generate_image(design_id: str, design_description: str, original_screenshot: Optional[str] = None) -> Dict:
    """
    调用图片生成 API，根据设计说明生成效果图
    
    Args:
        design_id: 设计记录ID
        design_description: 设计说明文本
        original_screenshot: 原始截图URL（可选，作为参考）
    
    Returns:
        包含状态和URL的字典:
        - success: 是否成功发起生成请求
        - task_id: 异步任务ID
        - message: 状态消息
    """
    if not settings.IMAGE_API_KEY or not settings.IMAGE_API_URL:
        logger.warning("图片生成API配置不完整，返回占位响应")
        return {
            "success": False,
            "task_id": None,
            "message": "图片生成API未配置，请检查环境变量"
        }
    
    prompt = _build_image_prompt(design_description, original_screenshot)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {settings.IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512,
                "seed": design_id
            }
            
            response = await client.post(settings.IMAGE_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get("id", design_id)
            image_url = result.get("output", [{}])[0] if result.get("output") else None
            
            logger.info(f"图片生成任务已提交，task_id: {task_id}")
            
            return {
                "success": True,
                "task_id": task_id,
                "message": "图片生成任务已提交",
                "image_url": image_url
            }
            
    except httpx.HTTPStatusError as e:
        logger.error(f"图片生成API调用失败: {e.response.status_code} - {e.response.text}")
        return {
            "success": False,
            "task_id": None,
            "message": f"图片生成失败: HTTP {e.response.status_code}"
        }
    except Exception as e:
        logger.error(f"图片生成API调用异常: {e}")
        return {
            "success": False,
            "task_id": None,
            "message": f"图片生成失败: {str(e)}"
        }


async def check_generation_status(task_id: str) -> Dict:
    """
    查询图片生成任务的状态
    
    Args:
        task_id: 异步任务ID
    
    Returns:
        包含状态和结果的字典:
        - status: 任务状态（pending/processing/completed/failed）
        - image_url: 生成的图片URL（完成时）
        - message: 状态消息
    """
    if not settings.IMAGE_API_KEY:
        return {
            "status": "completed",
            "image_url": "占位图片URL",
            "message": "API未配置，返回占位数据"
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {settings.IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {"task_id": task_id}
            
            response = await client.post(f"{settings.IMAGE_API_URL}/status", headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status", "pending")
            image_url = result.get("output", [{}])[0] if result.get("output") else None
            
            logger.info(f"任务状态查询，task_id: {task_id}, status: {status}")
            
            return {
                "status": status,
                "image_url": image_url,
                "message": f"任务状态: {status}"
            }
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"任务不存在，task_id: {task_id}")
            return {
                "status": "failed",
                "image_url": None,
                "message": "任务不存在或已过期"
            }
        logger.error(f"状态查询失败: {e.response.status_code} - {e.response.text}")
        return {
            "status": "failed",
            "image_url": None,
            "message": f"状态查询失败: {str(e)}"
        }
    except Exception as e:
        logger.error(f"状态查询异常: {e}")
        return {
            "status": "failed",
            "image_url": None,
            "message": f"状态查询异常: {str(e)}"
        }


def _build_image_prompt(design_description: str, original_screenshot: Optional[str] = None) -> str:
    """
    构建图片生成的提示词
    
    Args:
        design_description: 设计说明文本
        original_screenshot: 原始截图URL（可选）
    
    Returns:
        优化后的图片生成提示词
    """
    base_prompt = f"校园景观设计效果图，{design_description}，高质量，8K分辨率，专业摄影风格。"
    
    if original_screenshot:
        base_prompt += f"参考原始场景，保持校园建筑风格和整体氛围。"
    
    return base_prompt.strip()

