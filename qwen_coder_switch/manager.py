import json
import yaml
import typer
import random
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .api import check_api_key_validity
from .config import backup_config_file

console = Console()

def find_and_switch_key(provider_config_path: Path, qwen_config_path: Path, mode: str = "order") -> None:
    """
    遍历查找有效密钥并切换
    mode: 切换模式
        - order: 顺序切换 (默认)
        - reverse: 倒序切换
        - random: 随机切换
    """
    with open(provider_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if "provider" not in config:
        console.print("[red]✗[/red] 配置文件格式错误: 缺少 'provider' 根节点")
        return

    # 收集所有候选密钥
    candidates = []
    if "provider" in config and isinstance(config["provider"], dict):
        for provider_name, provider_config in config["provider"].items():
            if not isinstance(provider_config, dict):
                continue
                
            api_keys = provider_config.get("api_keys", [])
            base_url = provider_config.get("base_url")
            model_name = provider_config.get("model_name", "default-model")
            
            for key in api_keys:
                candidates.append({
                    "provider": provider_name,
                    "key": key,
                    "base_url": base_url,
                    "model_name": model_name
                })
    
    if not candidates:
        console.print("[red]✗[/red] 没有可用的 API 密钥")
        return

    # 根据模式调整顺序
    if mode == "random":
        random.shuffle(candidates)
        console.print(f"\n[bold cyan]开始查找有效密钥 (模式: 随机, 共 {len(candidates)} 个候选)...[/bold cyan]")
    elif mode == "reverse":
        candidates.reverse()
        console.print(f"\n[bold cyan]开始查找有效密钥 (模式: 倒序, 共 {len(candidates)} 个候选)...[/bold cyan]")
    else:
        # order (default) - keep as is
        console.print(f"\n[bold cyan]开始查找有效密钥 (模式: 顺序, 共 {len(candidates)} 个候选)...[/bold cyan]")
    
    modified = False
    valid_key_found = None
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("正在验证密钥...", total=len(candidates))
        
        for candidate in candidates:
            provider = candidate["provider"]
            key = candidate["key"]
            base_url = candidate["base_url"]
            model_name = candidate["model_name"]
            
            progress.update(task, description=f"验证 {provider} 密钥: {key[:10]}...")
            
            is_valid, should_remove = check_api_key_validity(provider, key, base_url, model_name)
            
            if is_valid:
                valid_key_found = candidate
                console.print(f"[green]✓[/green] 找到有效密钥: {provider} - {key[:15]}...")
                break # 找到一个就退出
            elif should_remove:
                # 标记为无效，需要从配置中删除
                console.print(f"[red]✗[/red] 移除无效密钥: {provider} - {key[:15]}...")
                
                # 从内存中的 config 删除
                if key in config["provider"][provider]["api_keys"]:
                     config["provider"][provider]["api_keys"].remove(key)
                     modified = True
            else:
                console.print(f"[yellow]⚠[/yellow] 密钥暂时不可用 (跳过): {provider} - {key[:15]}...")
            
            progress.advance(task)

    # 如果有修改，保存配置
    if modified:
        backup_config_file(provider_config_path)
        with open(provider_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            console.print("[blue]ℹ[/blue] 已更新 provider 配置文件 (移除无效密钥)")

    # 如果找到有效密钥，更新 qwen config
    if valid_key_found:
        _update_qwen_config(qwen_config_path, valid_key_found)
    else:
        console.print("[red]✗[/red] 未找到任何有效的 API 密钥")
        raise typer.Exit(1)

def _update_qwen_config(config_path: Path, key_info: Dict) -> None:
    """更新 Qwen 配置文件"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                qwen_config = json.load(f)
            except json.JSONDecodeError:
                 qwen_config = {}
    else:
        qwen_config = {}

    # Ensure structure exists
    if "$version" not in qwen_config:
        qwen_config["$version"] = 2
    if "security" not in qwen_config:
        qwen_config["security"] = {}
    if "auth" not in qwen_config["security"]:
        qwen_config["security"]["auth"] = {}
    if "model" not in qwen_config:
        qwen_config["model"] = {"name": ""}

    # 更新密钥
    qwen_config["security"]["auth"]["selectedType"] = "openai" 
    qwen_config["security"]["auth"]["apiKey"] = key_info["key"]
    qwen_config["security"]["auth"]["baseUrl"] = key_info["base_url"]
    qwen_config["model"]["name"] = key_info["model_name"]

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(qwen_config, f, indent=2, ensure_ascii=False)
    
    console.print(Panel(
        f"已切换到有效密钥:\n"
        f"供应商: [bold magenta]{key_info['provider']}[/bold magenta]\n"
        f"密钥: {key_info['key'][:15]}...",
        title="切换成功",
        border_style="green"
    ))
    console.print(f"[blue]ℹ[/blue] Qwen 配置文件: {config_path}")
