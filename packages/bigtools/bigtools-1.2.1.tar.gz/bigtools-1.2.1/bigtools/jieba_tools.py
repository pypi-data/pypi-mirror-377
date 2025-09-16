# -*- coding: UTF-8 -*-
# @Time : 2023/11/15 18:18 
# @Author : 刘洪波
import jieba
import asyncio
from bigtools.stopwords import stopwords


def get_keywords_from_text(text: str):
    """从文本中获取关键词"""
    return [i.strip() for i in jieba.cut(text) if i.strip() and i.strip() not in stopwords]


async def get_keywords_from_text_async(text: str):
    """异步从文本中获取关键词"""
    return await asyncio.to_thread(get_keywords_from_text,text)
