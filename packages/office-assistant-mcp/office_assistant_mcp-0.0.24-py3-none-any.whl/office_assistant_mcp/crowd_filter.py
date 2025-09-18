from typing import Dict, Any, Optional
from shared.coze_api import ask_coze_bot
from shared.log_util import log_info, log_error
from .crowd_filter_prompts import CREATE_CROWD_FILTER_PROMPT, MODIFY_CROWD_FILTER_PROMPT
import asyncio
import os

# 使用扣子API，还是原有的LLM
USE_COZE_BOT = True


def _convert_to_coze_question_for_create(
    product_title: str,
    product_id: str,
    brand: str,
    category_level4: str,
    expected_crowd_size: int,
    brand_repurch_period: int = 0,
    product_repurch_period: int = 0
) -> str:
    """将创建筛选条件的参数转换为适合Coze Agent的问题格式"""
    question = f"请为以下商品创建人群筛选条件：\n"
    question += f"商品：{product_title}（ID: {product_id}）\n"
    question += f"品牌：{brand}\n"
    question += f"四级类目：{category_level4}\n"
    if expected_crowd_size > 0:
        question += f"期望人群数：{expected_crowd_size}人\n"
    if brand_repurch_period > 0:
        question += f"品牌复购周期：{brand_repurch_period}天\n"
    if product_repurch_period > 0:
        question += f"商品复购周期：{product_repurch_period}天\n"
    
    question += "\n请直接给出筛选条件，格式为自然语言描述。"
    return question


def _convert_to_coze_question_for_modify(
    product_title: str,
    product_id: str,
    brand: str,
    category_level4: str,
    expected_crowd_size: int,
    original_filter: str,
    actual_crowd_size: int
) -> str:
    """将修改筛选条件的参数转换为适合Coze Agent的问题格式"""
    diff_ratio = abs(actual_crowd_size - expected_crowd_size) / expected_crowd_size if expected_crowd_size > 0 else 0
    
    question = f"请帮我优化人群筛选条件：\n"
    question += f"商品：{product_title}（ID: {product_id}）\n"
    question += f"品牌：{brand}\n"
    question += f"四级类目：{category_level4}\n"
    question += f"期望人群数：{expected_crowd_size}人\n"
    question += f"当前筛选条件：{original_filter}\n"
    question += f"实际圈定人数：{actual_crowd_size}人（差异{diff_ratio*100:.1f}%）\n"
    
    if diff_ratio < 0.1:
        question += "\n差异已在10%以内，是否需要继续优化？如果不需要，请回复'不再修改'。"
    else:
        question += f"\n请{'放宽' if actual_crowd_size < expected_crowd_size else '收紧'}条件，使人数接近期望值。"
    
    return question


def _send_llm_request_sync(prompt: str) -> str:
    """
    统一的LLM请求方法，支持切换不同的LLM服务
    
    Args:
        prompt: 提示词内容
        
    Returns:
        str: LLM响应内容
        
    Raises:
        Exception: 当LLM请求失败时
    """
    if USE_COZE_BOT:
        # 使用扣子API - 不直接传递原始prompt，而是转换为简洁问题
        # 原始prompt会传递到下层函数进行处理
        return ask_coze_bot(prompt)
    else:
        # 使用 playwright_util 的 send_llm_request (异步方法)
        from office_assistant_mcp.playwright_util import send_llm_request
        
        # 在同步函数中运行异步函数
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已经在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, send_llm_request(prompt))
                    return future.result()
            else:
                # 如果事件循环未运行，直接运行
                return loop.run_until_complete(send_llm_request(prompt))
        except RuntimeError:
            # 如果没有事件循环，创建新的
            return asyncio.run(send_llm_request(prompt))


def create_crowd_filter(
    product_title: str,
    product_id: str,
    brand: str,
    category_level4: str,
    expected_crowd_size: int,
    brand_repurch_period: int = 0,
    product_repurch_period: int = 0
) -> str:
    """创建人群筛选条件
    
    根据商品信息和期望的人群人数，生成自然语言描述的人群筛选条件。
    
    Args:
        product_title: 商品标题，不为空
        product_id: 商品ID，不为空
        brand: 品牌，不为空
        category_level4: 四级类目，不为空
        expected_crowd_size: 期望的人群人数
        brand_repurch_period: 品牌复购周期（天数），可选，默认为0（不使用）
        product_repurch_period: 商品复购周期（天数），可选，默认为0（不使用）
        
    Returns:
        str: 自然语言描述的人群筛选条件
        
    Raises:
        ValueError: 当输入参数为空时
        Exception: 当调用AI服务失败时
    """
    # 参数验证
    if not all([product_title, product_id, brand, category_level4]):
        raise ValueError("商品信息不能为空：商品标题、商品ID、品牌、四级类目均为必填项")
    
    if not isinstance(expected_crowd_size, int) or expected_crowd_size <= 0:
        raise ValueError("期望人群人数必须为正整数")
    
    try:
        log_info(f"开始创建人群筛选条件 - 商品: {product_title}, 品牌: {brand}, 类目: {category_level4}, 期望人数: {expected_crowd_size}")
        
        if USE_COZE_BOT:
            # 使用 Coze API 时，构建简洁的问题
            question = _convert_to_coze_question_for_create(
                product_title=product_title,
                product_id=product_id,
                brand=brand,
                category_level4=category_level4,
                expected_crowd_size=expected_crowd_size,
                brand_repurch_period=brand_repurch_period,
                product_repurch_period=product_repurch_period
            )
            result = _send_llm_request_sync(question)
        else:
            # 使用原有 LLM 时，构建完整的提示词
            # 构建复购周期信息字符串
            repurchase_cycle_info = ""
            if brand_repurch_period > 0:
                repurchase_cycle_info += f"\n- **品牌复购周期**: {int(brand_repurch_period)}天"
            if product_repurch_period > 0:
                repurchase_cycle_info += f"\n- **商品复购周期**: {int(product_repurch_period)}天"
            
            # 使用新的提示词模板
            prompt = CREATE_CROWD_FILTER_PROMPT.format(
                product_title=product_title,
                product_id=product_id,
                brand=brand,
                category_level4=category_level4,
                expected_crowd_size=expected_crowd_size,
                repurchase_cycle_info=repurchase_cycle_info
            )
            
            result = _send_llm_request_sync(prompt)
        
        log_info(f"人群筛选条件创建成功 (使用{'Coze' if USE_COZE_BOT else 'LLM'}): {result}")
        return result
        
    except Exception as e:
        log_error(f"创建人群筛选条件失败: {str(e)}")
        raise Exception(f"创建人群筛选条件失败: {str(e)}")


def modify_crowd_filter(
    product_title: str,
    product_id: str,
    brand: str,
    category_level4: str,
    expected_crowd_size: int,
    original_filter: str,
    actual_crowd_size: int
) -> str:
    """修改人群筛选条件
    
    根据原筛选条件的实际圈定人数与期望人数的差异，生成新的筛选条件或决定不再修改。
    
    Args:
        product_title: 商品标题
        product_id: 商品ID
        brand: 品牌
        category_level4: 四级类目
        expected_crowd_size: 期望人群数
        original_filter: 原筛选条件
        actual_crowd_size: 实际圈定的人数
        
    Returns:
        str: 新的筛选条件描述，或者"不再修改"
        
    Raises:
        ValueError: 当输入参数无效时
        Exception: 当调用AI服务失败时
    """
    # 参数验证
    if not all([product_title, product_id, brand, category_level4, original_filter]):
        raise ValueError("商品信息和原筛选条件不能为空")
    
    if not isinstance(expected_crowd_size, int) or expected_crowd_size <= 0:
        raise ValueError("期望人群人数必须为正整数")
        
    if not isinstance(actual_crowd_size, int) or actual_crowd_size < 0:
        raise ValueError("实际人群人数必须为非负整数")
    
    try:
        log_info(f"开始修改人群筛选条件 - 期望: {expected_crowd_size}, 实际: {actual_crowd_size}")
        
        # 计算差异比例
        if expected_crowd_size > 0:
            diff_ratio = abs(actual_crowd_size - expected_crowd_size) / expected_crowd_size
            if diff_ratio < 0.1:  # 差异小于10%，认为已经足够接近
                return "不再修改"
        
        if USE_COZE_BOT:
            # 使用 Coze API 时，构建简洁的问题
            question = _convert_to_coze_question_for_modify(
                product_title=product_title,
                product_id=product_id,
                brand=brand,
                category_level4=category_level4,
                expected_crowd_size=expected_crowd_size,
                original_filter=original_filter,
                actual_crowd_size=actual_crowd_size
            )
            result = _send_llm_request_sync(question)
        else:
            # 使用原有 LLM 时，构建完整的提示词
            prompt = MODIFY_CROWD_FILTER_PROMPT.format(
                product_title=product_title,
                product_id=product_id,
                brand=brand,
                category_level4=category_level4,
                expected_crowd_size=expected_crowd_size,
                original_filter=original_filter,
                actual_crowd_size=actual_crowd_size
            )
            
            result = _send_llm_request_sync(prompt)
        
        log_info(f"人群筛选条件修改结果 (使用{'Coze' if USE_COZE_BOT else 'LLM'}): {result}")
        return result
        
    except Exception as e:
        log_error(f"修改人群筛选条件失败: {str(e)}")
        raise Exception(f"修改人群筛选条件失败: {str(e)}")


def get_crowd_size_analysis(expected_size: int, actual_size: int) -> Dict[str, Any]:
    """分析人群规模差异
    
    Args:
        expected_size: 期望人群数
        actual_size: 实际人群数
        
    Returns:
        Dict: 包含差异分析的字典
    """
    if expected_size <= 0:
        return {"error": "期望人群数必须大于0"}
    
    diff = actual_size - expected_size
    diff_ratio = abs(diff) / expected_size
    
    if diff_ratio < 0.1:
        status = "接近目标"
    elif diff > 0:
        status = "超出目标"
    else:
        status = "低于目标"
    
    return {
        "expected_size": expected_size,
        "actual_size": actual_size,
        "difference": diff,
        "diff_ratio": round(diff_ratio * 100, 2),
        "status": status,
        "need_adjustment": diff_ratio >= 0.1
    }