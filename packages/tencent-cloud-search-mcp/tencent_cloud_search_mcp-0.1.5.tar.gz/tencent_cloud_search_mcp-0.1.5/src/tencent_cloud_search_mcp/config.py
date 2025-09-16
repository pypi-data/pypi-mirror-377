#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""配置管理模块"""

import os
from typing import Optional


class Config:
    """配置管理类"""

    def __init__(self):
        self.secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        self.endpoint = "wsa.tencentcloudapi.com"

    def validate(self) -> bool:
        """验证配置"""
        if not self.secret_id:
            raise ValueError("缺少TENCENTCLOUD_SECRET_ID环境变量")
        if not self.secret_key:
            raise ValueError("缺少TENCENTCLOUD_SECRET_KEY环境变量")
        return True

    def get_credentials(self) -> tuple[str, str]:
        """获取凭据"""
        return self.secret_id, self.secret_key