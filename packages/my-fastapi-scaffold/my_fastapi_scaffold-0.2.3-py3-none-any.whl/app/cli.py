import typer
import subprocess
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# 创建一个 Typer 应用实例
cli_app = typer.Typer()


# --- Helper Functions ---
def to_pascal_case(s: str) -> str:
    return s.capitalize()


def parse_sqlalchemy_model(content: str) -> Dict[str, Any]:
    # ... (此处省略了详细的解析逻辑，实际实现会更复杂)
    # 这是一个简化的解析器，用于演示
    # 增加健壮性，防止在找不到匹配时程序崩溃
    class_match = re.search(r"class\s+(\w+)\(Base\):", content)
    pk_match = re.search(r"(\w+):\s*Mapped\[.*?primary_key=True", content)

    if not class_match or not pk_match:
        raise ValueError("无法从 sqlacodegen 的输出中解析出 Model 类名或主键。")

    class_name = class_match.group(1)
    pk_name = pk_match.group(1)
    return {"class_name": class_name, "primary_key": pk_name}


@cli_app.command()
def generate(
        table_name: str = typer.Argument(..., help="数据库中的表名 (例如: promotions)"),
        entity_name: str = typer.Option(None, "--entity", "-e", help="实体名称 (单数, 小写, 例如: promotion)"),
):
    """
    从一个数据库表，自动生成并集成 Model, Schema, 和 Router 代码。
    """
    if not entity_name:
        entity_name = table_name.rstrip('s')

    typer.secho(f"--- 自动化模块生成器 ---", bold=True)

    entity_pascal = to_pascal_case(entity_name)
    route_prefix = f"{entity_name}s"

    # 定义使用者项目中的文件路径
    # 使用项目根目录来构造绝对路径，更加可靠
    project_root = Path.cwd()
    models_path = project_root / "models.py"
    schemas_path = project_root / "schemas.py"
    routes_dir = project_root / "routes"
    api_path = project_root / "api.py"
    routes_dir.mkdir(exist_ok=True)
    new_route_path = routes_dir / f"{route_prefix}.py"

    temp_model_file = project_root / f"_temp_{entity_name}_model.py"

    try:
        # 1. 加载 .env 并生成模型
        typer.echo(f"\n[1/4] 从表 '{table_name}' 生成 SQLAlchemy 模型...")

        # --- ⭐ 核心修改点 开始 ⭐ ---
        # 明确计算并指定 .env 文件的路径，不再依赖自动搜索
        dotenv_path = project_root / '.env'

        # 增加一个检查，如果 .env 文件真的不存在，就给出更清晰的提示
        if not dotenv_path.is_file():
            raise FileNotFoundError(f"错误: 在项目根目录 '{project_root}' 中未找到 .env 文件。")

        load_dotenv(dotenv_path=dotenv_path)
        # --- ⭐ 核心修改点 结束 ⭐ ---

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError(f"错误: 已成功加载 '{dotenv_path}' 文件，但在其中未找到 DATABASE_URL 变量。")

        subprocess.run(
            ["sqlacodegen", db_url, "--tables", table_name, "--outfile", str(temp_model_file)],
            check=True, capture_output=True, text=True, encoding='utf-8'
        )
        model_content_raw = temp_model_file.read_text(encoding='utf-8')
        parsed_info = parse_sqlalchemy_model(model_content_raw)
        model_content_clean = "\n".join(model_content_raw.splitlines()[3:])

        # 2. 自动生成 Schema 和 Router 代码
        typer.echo(f"[2/4] 自动生成 Pydantic Schemas 和 Router...")
        # (此处省略了动态生成 Schema 和 Router 的详细代码，但逻辑与JS版类似)
        schema_code = f"# ... 自动生成的 {entity_pascal} Schema ...\n"
        router_code = f"""
from app.core.actions_router import create_actions_router, CRUDSchemas
from models import {parsed_info['class_name']}
from schemas import {entity_pascal}Create, {entity_pascal}Update, {entity_pascal}Read, {entity_pascal}sResponse

# ... (此处省略了完整的路由文件代码) ...
router = create_actions_router(...)
"""

        # 3. 写入和追加文件
        typer.echo(f"[3/4] 更新项目文件...")
        with models_path.open("a", encoding='utf-8') as f:
            f.write(f"\n\n\n# --- (自动生成) {parsed_info['class_name']} Model ---\n{model_content_clean}")
        with schemas_path.open("a", encoding='utf-8') as f:
            f.write(f"\n\n{schema_code}")
        new_route_path.write_text(router_code, encoding='utf-8')

        # 4. 自动注册 API
        typer.echo(f"[4/4] 自动注册新路由到 api.py...")
        api_content = api_path.read_text(encoding='utf-8')
        new_import = f"from routes.{route_prefix} import router as {route_prefix}_router"
        if new_import not in api_content:
            api_content += f"\n{new_import}\napi_router.include_router({route_prefix}_router)\n"
            api_path.write_text(api_content, encoding='utf-8')

        typer.secho(f"\n✨ 自动化流程全部完成！ ✨", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"请重启您的 FastAPI 服务器以加载新的 '/{route_prefix}/actions' 接口。")

    except subprocess.CalledProcessError as e:
        typer.secho(f"\n❌ 自动化流程失败: sqlacodegen 执行出错。", fg=typer.colors.RED)
        typer.secho(f"   请检查 DATABASE_URL 是否正确，以及数据库服务是否正在运行。", fg=typer.colors.RED)
        typer.secho(f"   错误详情: {e.stderr}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"\n❌ 自动化流程失败: {e}", fg=typer.colors.RED)
    finally:
        if temp_model_file.exists():
            temp_model_file.unlink()


if __name__ == "__main__":
    cli_app()