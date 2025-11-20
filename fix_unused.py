import os
import re

TARGET_DIR = "src"


def remove_unused_imports(content):
    lines = content.split("\n")
    new_lines = []

    # detectar imports não usados
    for line in lines:
        if "import" in line and "unused" in line:
            continue
        new_lines.append(line)

    return "\n".join(new_lines)


def clean_variables_and_imports(content):
    # Remover variáveis não usadas simples
    content = re.sub(r"\s*[a-zA-Z_]+\s*=\s*[\w().]+\s*# unused\n", "", content)

    # Remover imports não usados (flake8 F401)
    content = re.sub(r"from [\w\.]+ import [\w, ]+  # unused\n", "", content)
    content = re.sub(r"import [\w\.]+  # unused\n", "", content)

    # Remover imports explícitos do relatório
    patterns = [
        r"from src\.colecao\.repository import listar_figurinhas_da_colecao.*",
        r"import random",
        r"from typing import Dict",
        r"from typing import List",
        r"from sqlalchemy import or_",
        r"from src\.colecao\.repository\.atualizar_colecao.*",
        r"from src\.colecao\.repository\.criar_colecao.*",
        r"from src\.colecao\.repository\.deletar_colecao.*",
        r"from src\.colecao\.repository\.get_colecao_by_id.*",
        r"from src\.colecao\.schema import FigurinhaAlbum",
        r"from src\.partidas\.schema import TimeInfo",
        r"from src\.usuario\.schema import LoginRequest",
        r"from typing import Optional",
        r"from jose import JWTError",
        r"from src\.usuario\.schema import UserResponse",
    ]

    for pattern in patterns:
        content = re.sub(pattern, "", content)

    return content


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    content = clean_variables_and_imports(content)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ cleaned {path}")
    else:
        print(f"- ok {path}")


def walk():
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))


if __name__ == "__main__":
    print("🚀 Limpando imports e variáveis não usadas...")
    walk()
    print("\n🎉 Limpeza completa! Execute agora:\n")
    print("python -m black .")
    print("python -m isort .")
    print("python -m flake8")
