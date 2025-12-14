import requests
from typing import Optional, Any, Tuple
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

def check_api_key_validity(
    provider: str, 
    api_key: str, 
    base_url: str, 
    model_name: str
) -> Tuple[bool, bool]:
    """检查 API 密钥是否有效 (通过简单对话测试)
    
    Args:
        provider: 供应商名称
        api_key: API Key
        base_url: API Base URL
        model_name: 模型名称
        
    Returns:
        Tuple[bool, bool]: (is_valid, should_remove)
    """
    if not base_url:
        return False, False

    try:
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        # 构造 chat completions URL
        chat_url = f"{base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user", 
                    "content": "hi"
                }
            ],
            "max_tokens": 1
        }
        
        try:
            response = requests.post(chat_url, headers=headers, json=payload, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            console.print(f"[yellow]![/yellow] 网络/连接错误 ({provider}): {str(e)}")
            return False, False # Network error, keep the key
        
        if response.status_code == 200:
            return True, False
            
        console.print(f"[yellow]![/yellow] API 测试失败 {response.status_code} ({provider}): {response.text[:100]}")
        # Typically 401/403 means invalid key. 429 means rate limit (keep). 5xx means server error (keep).
        # For simplicity based on user request "interface abnormal => delete", but user now added exception for network.
        # Let's be aggressive on delete for 4xx but conservative for others?
        # User said "Interface abnormal, delete invalid api_key".
        # But specifically asked to KEEP for ReadTimeout.
        
        if response.status_code in [401, 403]:
             return False, True # Definitely invalid
             
        if response.status_code == 429:
             return False, False # Rate limit, keep
             
        if response.status_code >= 500:
             return False, False # Server error, probably keep
             
        # Default for other errors (e.g. 400 bad request, 404 not found) -> Remove?
        # If "model not supported" (400), maybe remove or maybe config error. 
        # Better to remove so we find a working one.
        return False, True 
    
    except Exception as e:
        console.print(f"[red]✗[/red] 检查密钥时出错 ({provider}): {str(e)}")
        # Catch-all for other exceptions
        return False, False
