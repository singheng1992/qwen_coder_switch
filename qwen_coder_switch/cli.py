import typer
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from .constants import DEFAULT_PROVIDER_CONFIG, DEFAULT_QWEN_CONFIG
from .config import create_default_provider_config, validate_provider_config
from .manager import check_and_clean_keys, select_and_switch_key

app = typer.Typer(
    help="Qwen Coder API Key Manager", 
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()

@app.command()
def main(
    provider_config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="密钥配置文件路径"
    ),
    qwen_config: Optional[Path] = typer.Option(
        None,
        "--qwen-config", "-q",
        help="Qwen 配置文件路径"
    )
):
    """
    Qwen Coder API Key Manager - 管理和切换 API 密钥
    """
    console.print(Panel.fit(
        "[bold cyan]Qwen Coder API Key Manager[/bold cyan]\n"
        "管理和切换 AI 服务提供商 API 密钥",
        border_style="cyan"
    ))
    
    # 1. 检查密钥配置文件
    config_path = provider_config or DEFAULT_PROVIDER_CONFIG
    
    if provider_config and not config_path.exists():
        console.print(f"[red]✗[/red] 指定的配置文件不存在: {config_path}")
        raise typer.Exit(1)
    
    if not config_path.exists():
        console.print(f"[yellow]⚠[/yellow] 配置文件不存在: {config_path}")
        create_default_provider_config(config_path)
        raise typer.Exit(0)
    
    console.print(f"[green]✓[/green] 找到配置文件: {config_path}")
    
    # 2. 验证配置格式
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            provider_conf = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]✗[/red] 读取配置文件失败: {str(e)}")
        raise typer.Exit(1)
    
    if not validate_provider_config(provider_conf):
        raise typer.Exit(1)
    
    # 3. 检查并清理密钥
    provider_conf, key_stats = check_and_clean_keys(config_path)
    
    # 4. 选择并切换密钥
    qwen_config_path = qwen_config or DEFAULT_QWEN_CONFIG
    select_and_switch_key(key_stats, qwen_config_path)
    
    console.print("\n[bold green]✓ 操作完成![/bold green]")
