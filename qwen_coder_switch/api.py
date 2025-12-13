import requests
from typing import Optional, Any
from rich.console import Console

console = Console()

def get_nested_value(data: Any, path: str) -> Any:
    """Helper function to get nested value from dictionary using dot notation"""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current

def check_api_key_balance(
    provider: str, 
    api_key: str, 
    balance_url: str, 
    balance_field: str
) -> Optional[float]:
    """检查 API 密钥的余额
    
    Args:
        provider: 供应商名称
        api_key: API Key
        balance_url: 获取余额的 URL
        balance_field: 余额在响应 JSON 中的字段路径 (例如: data.balance)
    """
    if not balance_url:
        return None

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(balance_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            console.print(f"[yellow]![/yellow] HTTP {response.status_code} ({provider})")
            return None
        
        data = response.json()
        
        # 解析余额
        balance_value = get_nested_value(data, balance_field)
        
        if balance_value is not None:
            try:
                return float(balance_value)
            except (ValueError, TypeError):
                console.print(f"[red]✗[/red] 无法解析余额数值: {balance_value} ({provider})")
                return None
        
        return None
    
    except Exception as e:
        console.print(f"[red]✗[/red] 检查密钥时出错 ({provider}): {str(e)}")
        return None
