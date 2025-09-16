import os
import typer
import subprocess
from pathlib import Path
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# 创建一个 Typer 应用实例
cli_app = typer.Typer()


def to_pascal_case(s: str) -> str:
    """将 snake_case 或普通字符串转换为 PascalCase。"""
    return "".join(word.capitalize() for word in s.split('_'))


def get_db_url_from_env() -> str:
    """从 .env 文件安全地读取 DATABASE_URL。"""
    project_root = Path.cwd()
    dotenv_path = project_root / '.env'
    if not dotenv_path.is_file():
        raise FileNotFoundError(f"错误: 在项目根目录 '{project_root}' 中未找到 .env 文件。")

    load_dotenv(dotenv_path=dotenv_path)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(f"错误: 已成功加载 '{dotenv_path}' 文件，但在其中未找到 DATABASE_URL 变量。")
    return db_url


def parse_sqlalchemy_model(content: str) -> Dict[str, Any]:
    """一个更健壮的模型解析器，用于解析 sqlacodegen 的输出。"""
    class_name_match = re.search(r"class\s+(\w+)\(Base\):", content)
    if not class_name_match:
        raise ValueError("无法解析模型类名。")
    class_name = class_name_match.group(1)

    pk_match = re.search(r"(\w+):\s*Mapped\[.*?primary_key=True", content)
    if not pk_match:
        raise ValueError("无法解析主键。")
    primary_key = pk_match.group(1)

    fields = []
    # 解析 Mapped[type] 和 Mapped[Optional[type]] 两种形式
    for match in re.finditer(r"^\s*(\w+):\s*Mapped\[(Optional\[)?([\w\.]+)\]?", content, re.MULTILINE):
        field_name, is_optional, field_type = match.groups()
        if field_name == primary_key:
            continue
        fields.append({"name": field_name, "type": field_type, "optional": bool(is_optional)})

    return {"class_name": class_name, "primary_key": primary_key, "fields": fields}


def generate_schema_code(entity_pascal: str, pk_name: str, fields: List[Dict]) -> str:
    """根据解析出的字段，动态生成 Pydantic Schema 代码。"""

    def map_type(t: str) -> str:
        return {"str": "str", "int": "int", "float": "float", "date": "date", "datetime": "datetime"}.get(t, "Any")

    base_fields = "\n".join([f"    {f['name']}: Optional[{map_type(f['type'])}] = None" for f in fields])
    create_fields = "\n".join([f"    {f['name']}: {map_type(f['type'])}" for f in fields if not f['optional']])
    update_fields = "\n".join([f"    {f['name']}: Optional[{map_type(f['type'])}] = None" for f in fields])

    return f"""
# --- (自动生成) {entity_pascal} Schemas ---
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import date, datetime

class {entity_pascal}Base(BaseModel):
{base_fields if base_fields else '    pass'}

class {entity_pascal}Create({entity_pascal}Base):
{create_fields if create_fields else '    pass'}

class {entity_pascal}Update(BaseModel):
{update_fields if update_fields else '    pass'}

class {entity_pascal}Read({entity_pascal}Base):
    {pk_name}: int
    model_config = ConfigDict(from_attributes=True)

class {entity_pascal}sResponse(BaseModel):
    data: List[{entity_pascal}Read]
    total_count: int
"""


def generate_router_code(entity_name: str, model_name: str, pk_name: str) -> str:
    """动态生成完整的路由文件代码。"""
    entity_pascal = to_pascal_case(entity_name)
    return f"""
# --- (自动生成) {entity_pascal} Router ---
import logging
from fastapi import APIRouter

# 从库中导入核心工具
from app.core.actions_router import create_actions_router, CRUDSchemas
from app.core.logging_crud import LoggingFastCRUD

# 导入本项目的模型和 Schemas
from models import {model_name}
from schemas import (
    {entity_pascal}Create,
    {entity_pascal}Update,
    {entity_pascal}Read,
    {entity_pascal}sResponse,
)

logger = logging.getLogger(__name__)

# 准备 CRUD 实例和 Schema 集合
crud_instance = LoggingFastCRUD({model_name})
schemas = CRUDSchemas(
    Create={entity_pascal}Create,
    Update={entity_pascal}Update,
    Read={entity_pascal}Read,
    MultiResponse={entity_pascal}sResponse,
)

# 调用工厂函数，一键生成路由器
router = create_actions_router(
    crud_instance=crud_instance,
    schemas=schemas,
    prefix="/{entity_name}s",
    tags=["{entity_pascal}"],
    primary_key_name="{pk_name}"
)
"""


@cli_app.command("generate")
def generate_module(
        table_name: str = typer.Argument(..., help="数据库中的表名 (例如: promotions)"),
        entity_name: str = typer.Option(None, "--entity", "-e", help="实体名称 (单数, 小写, 例如: promotion)"),
):
    """从一个数据库表，自动生成并集成 Model, Schema, 和 Router 代码。"""
    if not entity_name:
        entity_name = table_name.rstrip('s')

    typer.secho(f"--- 自动化模块生成器 ---", bold=True)

    project_root = Path.cwd()
    temp_model_file = project_root / f"_temp_{entity_name}_model.py"

    try:
        # 1. 生成模型
        typer.echo(f"\n[1/5] 从表 '{table_name}' 生成 SQLAlchemy 模型...")
        db_url = get_db_url_from_env()
        command = ["sqlacodegen", db_url, "--tables", table_name, "--outfile", str(temp_model_file)]
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f"sqlacodegen 执行失败: {result.stderr}")

        # 2. 解析模型
        typer.echo(f"[2/5] 解析生成的模型...")
        model_content_raw = temp_model_file.read_text(encoding='utf-8')
        parsed_info = parse_sqlalchemy_model(model_content_raw)
        model_content_clean = "\\n".join(model_content_raw.splitlines()[3:])

        # 3. 生成 Schema
        typer.echo(f"[3/5] 自动生成 Pydantic Schemas...")
        schema_code = generate_schema_code(parsed_info['class_name'], parsed_info['primary_key'], parsed_info['fields'])

        # 4. 生成路由
        typer.echo(f"[4/5] 自动生成路由文件...")
        router_code = generate_router_code(entity_name, parsed_info['class_name'], parsed_info['primary_key'])

        # 5. 写入文件
        typer.echo(f"[5/5] 更新项目文件...")
        with open(project_root / "models.py", "a", encoding='utf-8') as f:
            f.write(f"\\n\\n\\n# --- (自动生成) {parsed_info['class_name']} Model ---\\n{model_content_clean}")
        typer.echo(f"  -> 已将模型追加到 models.py")

        with open(project_root / "schemas.py", "a", encoding='utf-8') as f:
            f.write(f"\\n\\n{schema_code}")
        typer.echo(f"  -> 已将 Schema 追加到 schemas.py")

        route_prefix = f"{entity_name}s"
        route_target_path = project_root / "routes" / f"{route_prefix}.py"
        route_target_path.parent.mkdir(exist_ok=True)
        route_target_path.write_text(router_code, encoding='utf-8')
        typer.echo(f"  -> 已创建路由文件: {route_target_path}")

        api_router_path = project_root / 'api.py'
        api_router_content = api_router_path.read_text(encoding='utf-8')
        new_import = f"from routes.{route_prefix} import router as {route_prefix}_router"
        if new_import not in api_router_content:
            new_inclusion = f"""
# --- (自动生成) 注册 {route_prefix} 路由 ---
api_router.include_router({route_prefix}_router)"""
            api_router_content += f"\\n{new_import}\n{new_inclusion}\\n"
            api_router_path.write_text(api_router_content, encoding='utf-8')
            typer.echo(f"  -> 已将新路由自动注册到 api.py")

        typer.secho(f"\\n✨ 自动化流程全部完成！ ✨", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"请重启您的 FastAPI 服务器以加载新的 '/{route_prefix}' 接口。")

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        typer.secho(f"\\n❌ 自动化流程失败: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"\\n❌ 发生未知错误: {e}", fg=typer.colors.RED)
    finally:
        if temp_model_file.exists():
            temp_model_file.unlink()


if __name__ == "__main__":
    cli_app()