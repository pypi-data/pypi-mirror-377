# -*- coding: UTF-8 -*-
# @Time : 2025/9/15 18:19 
# @Author : 刘洪波

import json
import logging
import asyncio
import aiofiles
from pathlib import Path
from typing import Any, Union, Optional, Tuple
from jsonschema import validate, ValidationError


async def save_json_data_async(
    json_data: Any,
    json_file_path: Union[str, Path],
    indent: int = 4,
    logger: logging.Logger = None
) -> bool:
    """
    异步保存 JSON 数据至文件
    - 在异步代码中使用 `await`，返回 bool

    :param json_data: 要保存的数据
    :param json_file_path: 文件路径（str 或 Path）
    :param indent: JSON 缩进
    :param logger: 日志对象，若为空则使用 print
    :return: 是否保存成功 (bool)
    """
    try:
        json_file_path = Path(json_file_path)
        json_file_path.parent.mkdir(parents=True, exist_ok=True)
        json_text = json.dumps(json_data, ensure_ascii=False, indent=indent)
        async with aiofiles.open(json_file_path, 'w', encoding='utf-8') as f:
            await f.write(json_text)
        if logger:
            logger.info(f"[async] JSON 数据已保存: {json_file_path}")
        else:
            print(f"[async] JSON 数据已保存: {json_file_path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"[async] 保存 JSON 数据失败: {e}", exc_info=True)
        else:
            print(f"[async] 保存 JSON 数据失败: {e}")
        return False


def save_json_data_sync(
    json_data: Any,
    json_file_path: Union[str, Path],
    indent: int = 4,
    logger: logging.Logger = None
) -> bool:
    """
    同步保存 JSON 数据至文件

    - 在同步代码中直接调用，返回 bool
    :param json_data: 要保存的数据
    :param json_file_path: 文件路径（str 或 Path）
    :param indent: JSON 缩进
    :param logger: 日志对象，若为空则使用 print
    :return: 是否保存成功 (bool)
    """
    try:
        json_file_path = Path(json_file_path)
        json_file_path.parent.mkdir(parents=True, exist_ok=True)
        with json_file_path.open('w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=indent)
        if logger:
            logger.info(f"[sync] JSON 数据已保存: {json_file_path}")
        else:
            print(f"[sync] JSON 数据已保存: {json_file_path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"[sync] 保存 JSON 数据失败: {e}", exc_info=True)
        else:
            print(f"[sync] 保存 JSON 数据失败: {e}")
        return False



def save_json_data(
    json_data: Any,
    json_file_path: Union[str, Path],
    indent: int = 4,
    logger: logging.Logger = None
):
    """
    保存 JSON 数据至文件（同步/异步通用）

    - 在同步代码中直接调用，返回 bool
    - 在异步代码中使用 `await`，返回 bool

    :param json_data: 要保存的数据
    :param json_file_path: 文件路径（str 或 Path）
    :param indent: JSON 缩进
    :param logger: 日志对象，若为空则使用 print
    :return: 是否保存成功 (bool)
    """
    json_file_path = Path(json_file_path)

    async def _save_async() -> bool:
        try:
            json_file_path.parent.mkdir(parents=True, exist_ok=True)
            json_text = json.dumps(json_data, ensure_ascii=False, indent=indent)
            async with aiofiles.open(json_file_path, 'w', encoding='utf-8') as f:
                await f.write(json_text)
            if logger:
                logger.info(f"[async] JSON 数据已保存: {json_file_path}")
            else:
                print(f"[async] JSON 数据已保存: {json_file_path}")
            return True
        except Exception as e:
            if logger:
                logger.error(f"[async] 保存 JSON 数据失败: {e}", exc_info=True)
            else:
                print(f"[async] 保存 JSON 数据失败: {e}")
            return False

    def _save_sync() -> bool:
        try:
            json_file_path.parent.mkdir(parents=True, exist_ok=True)
            with json_file_path.open('w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=indent)
            if logger:
                logger.info(f"[sync] JSON 数据已保存: {json_file_path}")
            else:
                print(f"[sync] JSON 数据已保存: {json_file_path}")
            return True
        except Exception as e:
            if logger:
                logger.error(f"[sync] 保存 JSON 数据失败: {e}", exc_info=True)
            else:
                print(f"[sync] 保存 JSON 数据失败: {e}")
            return False

    # 判断当前是否在异步事件循环中
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return _save_async()  # 返回 coroutine，需要 await
    except RuntimeError:
        pass  # 没有运行中的事件循环 -> 同步环境

    return _save_sync()  # 同步执行


async def load_json_data_async(json_file_path: Union[str, Path],
                               logger: Optional[logging.Logger] = None):
    """
    异步读取 JSON 数据
    - 异步调用：返回 coroutine，需要 await
    :param json_file_path: 文件路径（str 或 Path）
    :param logger: 日志对象，若为空则使用 print
    :return: 读取到的数据，失败时返回 None
    """
    try:
        json_file_path = Path(json_file_path)
        async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
            text = await f.read()
        data = json.loads(text)
        if logger:
            logger.info(f"[async] JSON 数据已读取: {json_file_path}")
        else:
            print(f"[async] JSON 数据已读取: {json_file_path}")
        return data
    except Exception as e:
        if logger:
            logger.error(f"[async] 读取 JSON 数据失败: {e}", exc_info=True)
        else:
            print(f"[async] 读取 JSON 数据失败: {e}")
        return None

def load_json_data_sync(json_file_path: Union[str, Path],
                        logger: Optional[logging.Logger] = None):
    """
    同步读取 JSON 数据（通用）
    - 同步调用：返回数据 or None
    :param json_file_path: 文件路径（str 或 Path）
    :param logger: 日志对象，若为空则使用 print
    :return: 读取到的数据，失败时返回 None
    """
    try:
        json_file_path = Path(json_file_path)
        with json_file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if logger:
            logger.info(f"[sync] JSON 数据已读取: {json_file_path}")
        else:
            print(f"[sync] JSON 数据已读取: {json_file_path}")
        return data
    except Exception as e:
        if logger:
            logger.error(f"[sync] 读取 JSON 数据失败: {e}", exc_info=True)
        else:
            print(f"[sync] 读取 JSON 数据失败: {e}")
        return None


def load_json_data(
    json_file_path: Union[str, Path],
    logger: Optional[logging.Logger] = None
):
    """
    读取 JSON 数据（同步/异步通用）

    - 同步调用：返回数据 or None
    - 异步调用：返回 coroutine，需要 await

    :param json_file_path: 文件路径（str 或 Path）
    :param logger: 日志对象，若为空则使用 print
    :return: 读取到的数据，失败时返回 None
    """
    json_file_path = Path(json_file_path)

    async def _load_async():
        try:
            async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
                text = await f.read()
            data = json.loads(text)
            if logger:
                logger.info(f"[async] JSON 数据已读取: {json_file_path}")
            else:
                print(f"[async] JSON 数据已读取: {json_file_path}")
            return data
        except Exception as e:
            if logger:
                logger.error(f"[async] 读取 JSON 数据失败: {e}", exc_info=True)
            else:
                print(f"[async] 读取 JSON 数据失败: {e}")
            return None

    def _load_sync():
        try:
            with json_file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            if logger:
                logger.info(f"[sync] JSON 数据已读取: {json_file_path}")
            else:
                print(f"[sync] JSON 数据已读取: {json_file_path}")
            return data
        except Exception as e:
            if logger:
                logger.error(f"[sync] 读取 JSON 数据失败: {e}", exc_info=True)
            else:
                print(f"[sync] 读取 JSON 数据失败: {e}")
            return None

    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return _load_async()
    except RuntimeError:
        pass

    return _load_sync()


def pretty_print_json(json_data: Any, indent: int = 4) -> str:
    """返回格式化的 JSON 字符串（美化输出）"""
    return json.dumps(json_data, ensure_ascii=False, indent=indent)


def validate_json_string(json_string: str) -> bool:
    """验证字符串是否是合法 JSON"""
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def validate_json_schema(schema: dict, json_data: dict) -> Tuple[bool, ValidationError | None]:
    """
    验证 json 是否符合模板规定的格式
    :param schema: JSON Schema 模板
    :param json_data: 待验证的 JSON 数据
    :return: (是否符合, 错误对象或 None)
    """
    try:
        validate(instance=json_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, e