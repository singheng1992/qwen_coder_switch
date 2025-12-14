import typer
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from .constants import DEFAULT_PROVIDER_CONFIG, DEFAULT_QWEN_CONFIG
from .config import create_default_provider_config, validate_provider_config, restore_from_backup
from .manager import find_and_switch_key

app = typer.Typer(
    help="Qwen Coder API Key Manager", 
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()

def _run_switch_logic(provider_config: Path, qwen_config: Path, mode: str):
    """Execution logic for switching keys"""
    # 1. 检查密钥配置文件
    config_path = provider_config
    
    if not config_path.exists():
        # 如果是默认路径且不存在，创建它
        if config_path == DEFAULT_PROVIDER_CONFIG:
            console.print(f"[yellow]⚠[/yellow] 配置文件不存在: {config_path}")
            create_default_provider_config(config_path)
            raise typer.Exit(0)
        else:
             console.print(f"[red]✗[/red] 指定的配置文件不存在: {config_path}")
             raise typer.Exit(1)
    
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
    
    # 3. 查找并切换有效密钥
    find_and_switch_key(config_path, qwen_config, mode)
    
    console.print("\n[bold green]✓ 操作完成![/bold green]")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    provider_config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="密钥配置文件路径"
    ),
    qwen_config: Optional[Path] = typer.Option(
        None,
        "--qwen-config", "-q",
        help="Qwen 配置文件路径"
    ),
    mode: str = typer.Option(
        "order",
        "--mode", "-m",
        help="切换模式: order(顺序), reverse(倒序), random(随机)"
    )
):
    """
    Qwen Coder API Key Manager - 管理和切换 API 密钥
    """
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold cyan]Qwen Coder API Key Manager[/bold cyan]\n"
            "管理和切换 AI 服务提供商 API 密钥",
            border_style="cyan"
        ))
        
        # 使用默认值如果未提供
        config_path = provider_config or DEFAULT_PROVIDER_CONFIG
        qwen_path = qwen_config or DEFAULT_QWEN_CONFIG
        
        _run_switch_logic(config_path, qwen_path, mode)

@app.command()
def restore(
    provider_config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="密钥配置文件路径"
    )
):
    """
    从最近的备份恢复配置文件
    """
    config_path = provider_config or DEFAULT_PROVIDER_CONFIG
    
    console.print(f"[bold cyan]正在尝试恢复配置文件: {config_path}[/bold cyan]")
    
    if restore_from_backup(config_path):
        console.print("[bold green]恢复成功![/bold green]")
    else:
        raise typer.Exit(1)
