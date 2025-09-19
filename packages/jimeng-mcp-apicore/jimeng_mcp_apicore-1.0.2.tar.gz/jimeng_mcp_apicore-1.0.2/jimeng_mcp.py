#!/usr/bin/env python3
"""
即梦AI MCP 服务器 - APICore渠道版
通过 APICore 平台调用即梦AI (Doubao Seedream 4.0)
支持所有官方API功能
"""

import os
import httpx
from typing import Optional, Union, List, Dict, Any, Literal
from fastmcp import FastMCP
from image_processor import ImageProcessor

# 创建 FastMCP 实例
mcp = FastMCP("jimeng")

# API配置
API_BASE_URL = "https://api.apicore.ai/v1/images/generations"
API_KEY = os.getenv("APICORE_API_KEY", "")
OUTPUT_DIR = os.getenv("JIMENG_OUTPUT_DIR")

# 创建图片处理器实例
image_processor = ImageProcessor(output_dir=OUTPUT_DIR, provider="jimeng")

@mcp.tool()
async def jimeng(
    prompt: Union[str, List[str]],
    image: Optional[Union[str, List[str]]] = None,
    size: str = "1:1",
    n: int = 1,
    watermark: bool = False,
    stream: bool = False,
    style: Optional[Literal["realistic", "anime", "cartoon", "watercolor", 
                           "oil_painting", "sketch", "chinese_painting"]] = None,
    quality: Literal["draft", "standard", "high"] = "standard",
    sequential_image_generation: Optional[Literal["auto", "disabled"]] = "disabled",
    max_images: int = 15,
    response_format: Literal["url", "b64_json"] = "url"
) -> Dict[str, Any]:
    """
    即梦AI图片生成 (APICore渠道) - Doubao Seedream 4.0
    
    使用方式：
    1. 文生图：jimeng("一只猫")
    2. 图生图：jimeng("改为夜晚", image="http://...")
    3. 多参考图：jimeng("融合风格", image=["url1", "url2"])  
    4. 批量生成：jimeng("猫", n=4)
    5. 组图生成（重要）：
       - jimeng("生成3张不同角度的猫咪", sequential_image_generation="auto", max_images=3)
       - auto模式会根据prompt自动判断生成组图
       - max_images控制最多生成几张（1-15）
       - 提示词中明确说明数量效果更好，如"生成3张..."、"早中晚三个时间段"
    6. 多prompt批量：jimeng(["猫", "狗", "兔子"])
    
    参数：
        prompt: 描述文本（字符串或列表，最大1000字符）
        image: 参考图片URL（支持单张或多张）
        size: 图片尺寸（1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 21:9 等宽高比）
        n: 每个prompt生成数量（1-4）
        watermark: 是否添加水印
        stream: 是否流式传输（实时返回进度）
        style: 预设艺术风格
        quality: 生成质量（draft快速预览/standard标准/high高质量）
        sequential_image_generation: 组图模式
            - "auto": 自动判断生成组图，根据prompt内容决定数量
            - "disabled": 仅生成单张图片（默认）
            使用auto时，通过max_images参数控制最多生成几张（1-15）
            建议在prompt中明确说明需要的数量，如"生成5张不同风格的..."
        max_images: 组图最大数量（1-15，默认15，参考图+生成图总数≤15）
        response_format: 响应格式（url返回链接/b64_json返回base64）
    
    特色功能：
        - 原生高分辨率输出（最高4K）
        - 强大的中英文理解能力
        - 精准的小文字生成
        - 优秀的布局效果
        - 快速推理（比3.0快10倍）
    
    图片自动保存到本地目录！
    """
    
    # 多个不同prompt的批量生成
    if isinstance(prompt, list):
        results = []
        for i, p in enumerate(prompt, 1):
            print(f"批量处理 [{i}/{len(prompt)}]: {p[:30]}...")
            result = await _generate_single(
                p, image, size, n, watermark, stream, style, 
                quality, sequential_image_generation, max_images, 
                response_format
            )
            results.append({
                "prompt": p,
                "success": result.get("success", False),
                "images": result.get("local_images", []),
                "error": result.get("error") if not result.get("success") else None
            })
        
        # 统计成功率
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "mode": "多prompt批量",
            "total_prompts": len(prompt),
            "success_count": success_count,
            "failed_count": len(prompt) - success_count,
            "results": results,
            "output_dir": image_processor.output_dir
        }
    
    # 单个prompt生成
    return await _generate_single(
        prompt, image, size, n, watermark, stream, style,
        quality, sequential_image_generation, max_images, 
        response_format
    )


async def _generate_single(
    prompt: str,
    image_url: Optional[Union[str, List[str]]],
    size: str,
    n: int,
    watermark: bool,
    stream: bool,
    style: Optional[str],
    quality: str,
    sequential_image_generation: Optional[str],
    max_images: int,
    response_format: str
) -> Dict[str, Any]:
    """生成图片的核心函数"""
    
    if not API_KEY:
        return {
            "success": False,
            "error": "请设置环境变量 APICORE_API_KEY",
            "hint": "export APICORE_API_KEY='sk-your-key'"
        }
    
    # 参数验证
    if len(prompt) > 1000:
        return {
            "success": False,
            "error": "参数错误：prompt长度不能超过1000字符"
        }
    
    if n < 1 or n > 4:
        return {
            "success": False,
            "error": "参数错误：n必须在1-4之间"
        }
    
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 尺寸映射（将宽高比转换为像素值）
    size_mapping = {
        "1:1": "2048x2048",
        "4:3": "2304x1728",
        "3:4": "1728x2304",
        "16:9": "2560x1440",
        "9:16": "1440x2560",
        "3:2": "2496x1664",
        "2:3": "1664x2496",
        "21:9": "3024x1296"
    }
    
    # 如果传入的是比例格式，转换为像素值
    if size in size_mapping:
        actual_size = size_mapping[size]
    else:
        # 保持向后兼容，支持直接传入像素值
        actual_size = size
    
    # 构建请求体（必需参数）
    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "size": actual_size,
        "watermark": watermark,
        "stream": stream,
        "response_format": response_format
    }
    
    # 处理组图生成
    if sequential_image_generation == "auto":
        # 组图模式
        payload["sequential_image_generation"] = "auto"
        # 验证max_images范围
        if max_images < 1 or max_images > 15:
            return {
                "success": False,
                "error": "参数错误：max_images必须在1-15之间"
            }
        # 检查参考图数量限制
        ref_count = len(image_url) if isinstance(image_url, list) else (1 if image_url else 0)
        if ref_count + max_images > 15:
            return {
                "success": False,
                "error": f"参数错误：参考图({ref_count}张) + 生成图({max_images}张) 总数不能超过15张",
                "hint": f"请减少max_images到{15 - ref_count}或更少"
            }
        payload["sequential_image_generation_options"] = {
            "max_images": max_images
        }
    else:
        # 单图模式或批量模式
        payload["sequential_image_generation"] = "disabled"
        if n > 1:
            payload["n"] = n
    
    # 处理图生图（支持单张或多张参考图）
    if image_url:
        if isinstance(image_url, list):
            payload["image"] = image_url  # 多张参考图
        else:
            payload["image"] = image_url  # 单张参考图
    
    # 可选参数
    if style:
        payload["style"] = style
    
    if quality != "standard":
        payload["quality"] = quality
    
    
    try:
        # 确定生成模式和预期数量
        if sequential_image_generation == "auto":
            mode = "组图生成"
            expected_count = max_images
        elif image_url:
            if isinstance(image_url, list):
                mode = f"多参考图生图（{len(image_url)}张参考）"
            else:
                mode = "图生图"
            expected_count = n
        else:
            mode = "文生图"
            expected_count = n
        
        # 打印生成信息
        print(f"🎨 {mode}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
        if expected_count > 1:
            print(f"   预期生成: {expected_count}张")
        if style:
            print(f"   艺术风格: {style}")
        if quality != "standard":
            print(f"   生成质量: {quality}")
        
        async with httpx.AsyncClient() as client:
            # 根据生成模式和质量调整超时时间
            timeout = 60.0  # 基础超时
            if quality == "high":
                timeout += 30.0
            if expected_count > 2:
                timeout += 30.0
            if sequential_image_generation == "auto":
                timeout += 60.0
            if size in ["2K", "4K", "2048x2048"]:
                timeout += 30.0
            
            response = await client.post(
                API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # 处理错误响应
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_info = error_data.get("error", {})
                    
                    # 特殊处理常见错误
                    error_code = error_info.get("code", "")
                    error_msg = error_info.get("message", "")
                    
                    if error_code == "ModelNotOpen":
                        return {
                            "success": False,
                            "error": "模型未开通",
                            "message": "请在APICore控制台确认已开通 doubao-seedream-4-0 服务",
                            "detail": error_msg
                        }
                    elif "rate_limit" in error_code.lower():
                        return {
                            "success": False,
                            "error": "速率限制",
                            "message": "请求过于频繁，请稍后重试",
                            "detail": error_msg
                        }
                    elif "invalid_api_key" in error_code.lower():
                        return {
                            "success": False,
                            "error": "API密钥无效",
                            "message": "请检查APICORE_API_KEY是否正确",
                            "detail": error_msg
                        }
                    
                    return {
                        "success": False,
                        "error": f"API错误 {response.status_code}",
                        "code": error_code,
                        "message": error_msg
                    }
                except:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "detail": response.text[:500]
                    }
            
            result = response.json()
            
            # 解析成功响应
            if "data" in result and result["data"]:
                images = result["data"]
                response_data = {
                    "success": True,
                    "mode": mode,
                    "prompt": prompt,
                    "generated_count": len(images),
                    "images": [],
                    "parameters": {
                        "model": "doubao-seedream-4-0-250828",
                        "size": size if size in size_mapping else actual_size,
                        "quality": quality,
                        "style": style,
                        "sequential": sequential_image_generation
                    },
                    "usage": result.get("usage", {}),
                    "created": result.get("created"),
                    "id": result.get("id")
                }
                
                # 处理每张图片
                for img in images:
                    img_data = {
                        "url": img.get("url", ""),
                        "width": img.get("width", 0),
                        "height": img.get("height", 0)
                    }
                    
                    # 如果有revised_prompt，添加到图片信息
                    if img.get("revised_prompt"):
                        img_data["revised_prompt"] = img["revised_prompt"]
                    
                    # 如果是base64格式
                    if response_format == "b64_json" and img.get("b64_json"):
                        img_data["b64_json"] = img["b64_json"]
                    
                    response_data["images"].append(img_data)
                
                # 自动下载并保存图片
                response_data = await image_processor.process_response(response_data)
                
                # 添加成功消息
                if response_data.get("local_images"):
                    count = len(response_data['local_images'])
                    response_data["message"] = f"✅ 成功生成并保存 {count} 张图片到 {image_processor.output_dir}"
                
                return response_data
            
            # 无数据返回
            return {
                "success": False,
                "error": "API返回空数据",
                "detail": result
            }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "⏱️ 请求超时",
            "hint": f"{mode}需要较长时间，建议：\n1. 减少生成数量\n2. 降低分辨率\n3. 使用draft质量进行测试"
        }
    except httpx.ConnectError:
        return {
            "success": False,
            "error": "🔌 连接失败",
            "hint": "请检查网络连接或API服务状态"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ 意外错误",
            "detail": str(e)
        }


def run_server():
    """入口函数，用于命令行调用"""
    mcp.run()

if __name__ == "__main__":
    run_server()