# model3d_service.py — 3D模型转换业务逻辑
# 职责：调用3D模型转换API，将效果图转换为3D模型

import httpx
from typing import Dict, Optional

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def convert_to_3d(image_url: str, design_id: str) -> Dict:
    """
    调用3D模型转换API，将2D效果图转换为3D模型
    
    Args:
        image_url: 待转换的2D效果图URL
        design_id: 设计记录ID
    
    Returns:
        包含转换状态的字典:
        - success: 是否成功发起转换请求
        - model_id: 3D模型ID
        - model_url: 3D模型下载URL（完成时）
        - message: 状态消息
    """
    if not settings.IMAGE_API_KEY:
        logger.warning("3D转换API配置不完整，返回占位响应")
        return {
            "success": False,
            "model_id": None,
            "model_url": None,
            "message": "3D转换API未配置，请检查环境变量"
        }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            headers = {
                "Authorization": f"Bearer {settings.IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "image_url": image_url,
                "output_format": "glb",
                "quality": "medium",
                "seed": design_id
            }
            
            response = await client.post(f"{settings.IMAGE_API_URL}/3d", headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            model_id = result.get("id", design_id)
            model_url = result.get("output", {}).get("url") if result.get("output") else None
            
            logger.info(f"3D模型转换任务已提交，model_id: {model_id}")
            
            return {
                "success": True,
                "model_id": model_id,
                "model_url": model_url,
                "message": "3D模型转换任务已提交"
            }
            
    except httpx.HTTPStatusError as e:
        logger.error(f"3D转换API调用失败: {e.response.status_code} - {e.response.text}")
        return {
            "success": False,
            "model_id": None,
            "model_url": None,
            "message": f"3D转换失败: HTTP {e.response.status_code}"
        }
    except Exception as e:
        logger.error(f"3D转换API调用异常: {e}")
        return {
            "success": False,
            "model_id": None,
            "model_url": None,
            "message": f"3D转换失败: {str(e)}"
        }


async def check_3d_status(model_id: str) -> Dict:
    """
    查询3D模型转换任务的状态
    
    Args:
        model_id: 3D模型任务ID
    
    Returns:
        包含状态和结果的字典:
        - status: 任务状态（pending/processing/completed/failed）
        - model_url: 3D模型下载URL（完成时）
        - message: 状态消息
    """
    if not settings.IMAGE_API_KEY:
        return {
            "status": "completed",
            "model_url": "占位3D模型URL",
            "message": "API未配置，返回占位数据"
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {settings.IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {"model_id": model_id}
            
            response = await client.post(f"{settings.IMAGE_API_URL}/3d/status", headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status", "pending")
            model_url = result.get("output", {}).get("url") if result.get("output") else None
            
            logger.info(f"3D模型转换状态查询，model_id: {model_id}, status: {status}")
            
            return {
                "status": status,
                "model_url": model_url,
                "message": f"3D模型转换状态: {status}"
            }
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"3D模型不存在，model_id: {model_id}")
            return {
                "status": "failed",
                "model_url": None,
                "message": "模型不存在或已过期"
            }
        logger.error(f"3D模型状态查询失败: {e.response.status_code} - {e.response.text}")
        return {
            "status": "failed",
            "model_url": None,
            "message": f"状态查询失败: {str(e)}"
        }
    except Exception as e:
        logger.error(f"3D模型状态查询异常: {e}")
        return {
            "status": "failed",
            "model_url": None,
            "message": f"状态查询异常: {str(e)}"
        }
