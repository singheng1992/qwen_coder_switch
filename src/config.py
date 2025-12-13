import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict
from rich.console import Console

console = Console()

def create_default_provider_config(path: Path) -> None:
    """创建默认的密钥配置文件"""
    default_config = {
        "provider": {
            "siliconflow": [
                "sk-your-api-key-here"
            ],
            "dmxapi": [
                "sk-your-api-key-here"
            ]
        }
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    
    console.print(f"[green]✓[/green] 已创建默认配置文件: {path}")
    console.print("[yellow]⚠[/yellow] 请编辑配置文件添加您的 API 密钥")


def validate_provider_config(config: Dict) -> bool:
    """验证密钥配置格式是否正确"""
    if "provider" not in config:
        console.print("[red]✗[/red] 配置文件格式错误: 缺少 'provider' 根节点")
        return False
    
    if not isinstance(config["provider"], dict):
        console.print("[red]✗[/red] 配置文件格式错误: 'provider' 应该是一个字典")
        return False
    
    for provider_name, api_keys in config["provider"].items():
        if not isinstance(api_keys, list):
            console.print(f"[red]✗[/red] 配置文件格式错误: '{provider_name}' 的值应该是一个列表")
            return False
        
        if not all(isinstance(key, str) for key in api_keys):
            console.print(f"[red]✗[/red] 配置文件格式错误: '{provider_name}' 中的 API 密钥应该都是字符串")
            return False
    
    console.print("[green]✓[/green] 配置文件格式验证通过")
    return True


def backup_config_file(path: Path) -> None:
    """备份配置文件"""
    if not path.exists():
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
    shutil.copy2(path, backup_path)
    console.print(f"[blue]ℹ[/blue] 已备份配置文件到: {backup_path}")
