import json
import yaml
import typer
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .api import check_api_key_balance
from .config import backup_config_file

console = Console()

def check_and_clean_keys(config_path: Path) -> Tuple[Dict, List[Dict]]:
    """检查所有密钥额度并清理无效密钥"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    valid_keys = {}
    invalid_keys = []
    key_stats = []
    modified = False
    
    console.print("\n[bold cyan]检查 API 密钥余额...[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for provider_name, api_keys in config["provider"].items():
            valid_keys[provider_name] = []
            
            for api_key in api_keys:
                task = progress.add_task(f"检查 {provider_name} 密钥...", total=None)
                
                balance = check_api_key_balance(provider_name, api_key)
                
                if balance is None:
                    console.print(f"[red]✗[/red] {provider_name}: {api_key[:15]}... - 无效或异常")
                    invalid_keys.append((provider_name, api_key))
                    modified = True
                elif balance <= 0:
                    console.print(f"[yellow]✗[/yellow] {provider_name}: {api_key[:15]}... - 余额不足 (¥{balance})")
                    invalid_keys.append((provider_name, api_key))
                    modified = True
                else:
                    console.print(f"[green]✓[/green] {provider_name}: {api_key[:15]}... - 余额充足 (¥{balance})")
                    valid_keys[provider_name].append(api_key)
                    key_stats.append({
                        "provider": provider_name,
                        "key": api_key,
                        "balance": balance
                    })
                
                progress.remove_task(task)
    
    # 如果有修改，备份并保存新配置
    if modified:
        backup_config_file(config_path)
        
        # 移除空的供应商
        valid_keys = {k: v for k, v in valid_keys.items() if v}
        
        new_config = {"provider": valid_keys}
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        
        console.print(f"\n[green]✓[/green] 已清理 {len(invalid_keys)} 个无效密钥")
    
    return (new_config if modified else config), key_stats


def select_and_switch_key(key_stats: List[Dict], qwen_config_path: Path) -> None:
    """自动选择余额最高的密钥并切换到 Qwen 配置"""
    if not key_stats:
        console.print("[red]✗[/red] 没有可用的 API 密钥")
        raise typer.Exit(1)
    
    # 按余额降序排序
    key_stats.sort(key=lambda x: x["balance"], reverse=True)
    
    # 选择余额最高的
    best_key_info = key_stats[0]
    selected_provider = best_key_info["provider"]
    selected_key = best_key_info["key"]
    max_balance = best_key_info["balance"]
    
    console.print(Panel(
        f"自动选择余额最高的密钥:\n"
        f"供应商: [bold magenta]{selected_provider}[/bold magenta]\n"
        f"余额: [bold green]¥{max_balance}[/bold green]\n"
        f"密钥: {selected_key[:15]}...",
        title="自动切换",
        border_style="green"
    ))
    
    # 获取 baseUrl
    base_url = "https://api.siliconflow.cn/"
    if selected_provider == "siliconflow":
        base_url = "https://api.siliconflow.cn/"
    # 根据需要添加其他供应商的 base URL
    
    # 读取并更新 Qwen 配置
    qwen_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if qwen_config_path.exists():
        with open(qwen_config_path, 'r', encoding='utf-8') as f:
            qwen_config = json.load(f)
    else:
        qwen_config = {
            "$version": 2,
            "security": {
                "auth": {
                    "selectedType": "openai"
                }
            },
            "model": {
                "name": "zai-org/GLM-4.6"
            }
        }
    
    # 更新密钥
    qwen_config["security"]["auth"]["apiKey"] = selected_key
    qwen_config["security"]["auth"]["baseUrl"] = base_url
    
    # 保存配置
    
    with open(qwen_config_path, 'w', encoding='utf-8') as f:
        json.dump(qwen_config, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[green]✓[/green] 已切换到 {selected_provider} 的密钥")
    console.print(f"[blue]ℹ[/blue] 配置文件: {qwen_config_path}")
