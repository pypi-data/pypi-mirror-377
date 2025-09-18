import os
from typing import Optional

from mcp.server import FastMCP
import requests

mcp = FastMCP("puppy mcp server")

auth_token = os.getenv('BACKSTAGE_AUTH_TOKEN') # 从环境变量中获取authToken
env = os.getenv('ACTIVE_ENV', 'test')  # 环境名，默认为test环境
if env == 'prod':
    api_url = "http://gateway.geojoyowo.net"
elif env == 'pre':
    api_url = "http://pregateway.geojoyowo.net"
else:
    api_url = "http://test1gateway.geojoyowo.net"  # 默认URL

@mcp.tool()
def hello_world():
    """测试服务是否正常"""
    return "hello world"

@mcp.tool()
def get_products(biz_enable: Optional[bool] = None, supplier_enable: Optional[bool] = None) -> list:
    """
    获取GEO产品列表
    
    Args:
        biz_enable: 商务合同可用
        supplier_enable: 供应商合同可用
    """
    url = f"{api_url}/geobackstage/product/select"

    headers = {
        "authToken": auth_token
    }

    # 请求体包含传入的参数
    data = {"bizEnable": biz_enable, "supplierEnable": supplier_enable}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["data"]
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []


def main():
    """启动MCP服务"""
    mcp.run()


if __name__ == "__main__":
    main()
