import requests
from typing import Optional
from rich.console import Console
from .provider import PROVIDER_ENDPOINTS

console = Console()

def check_api_key_balance(provider: str, api_key: str) -> Optional[float]:
    """检查 API 密钥的余额"""
    endpoint = PROVIDER_ENDPOINTS.get(provider, PROVIDER_ENDPOINTS.get("siliconflow"))
    # Fallback to siliconflow if provider not found, relying on provider.py's content
    
    if not endpoint:
        # 如果没有配置 endpoint，可能无法检查
        return None

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # 解析余额
        if data.get("code") == 20000 and "data" in data:
            balance_str = data["data"].get("balance", "0")
            return float(balance_str)
        
        return None
    
    except Exception as e:
        console.print(f"[red]✗[/red] 检查密钥时出错 ({provider}): {str(e)}")
        return None
