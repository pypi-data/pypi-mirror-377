#!/usr/bin/env python3

__author__ = "xi"
__all__ = [
    "TextAugmentationRequest",
    "TextAugmentationResponse",
    "TextAugmentationAsQueryRequest",
    "TextAugmentationAsKeywordsRequest",
    "TextAugmentationAsSummaryRequest",
]

from typing import Dict, Optional

from pydantic import Field

from agent_types.common import Request, Response


class TextAugmentationRequest(Request):
    """知识文本增强"""

    __request_name__ = "augment_text"

    text: str = Field(
        title="要切分的文本",
        description="一般是文档解析后返回的内容。"
    )
    text_type: str = Field(
        title="文本内容类型",
        description="文本内容类型, 例如：`md`, `txt`, `json`",
        default="md"
    )
    metadata: Optional[Dict] = Field(
        title="文档对应的metadata",
        description="文档对应的metadata",
        default_factory=dict
    )
    custom_rules: Optional[str] = Field(
        title="用户自定义切分规则",
        description="用户使用自然语言描述的切分规则，将用作大模型提示词的一部分。",
        default=None
    )


class TextAugmentationResponse(Response):
    """知识文本增强"""

    result: str = Field(
        title="文本增强结果",
        description="文本增强结果"
    )


class TextAugmentationAsQueryRequest(TextAugmentationRequest):
    """增强为相关查询（反向变换）"""

    __request_name__ = "augment_text_as_query"


class TextAugmentationAsKeywordsRequest(TextAugmentationRequest):
    """增强为关键字"""

    __request_name__ = "augment_text_as_keywords"


class TextAugmentationAsSummaryRequest(TextAugmentationRequest):
    """增强为总结"""

    __request_name__ = "augment_text_as_summary"
