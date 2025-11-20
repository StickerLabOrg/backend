import os
import subprocess

import autopep8

IGNORE_DIRS = ["venv", "__pycache__", "migrations", "alembic"]


def should_skip(path: str):
    return any(skip in path for skip in IGNORE_DIRS)


def clean_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Corrigir == True e == False
        content = content.replace("== True", "")
        content = content.replace("== False", "not ")

        # Corrigir "is True" / "is False"
        content = content.replace("is True", "")
        content = content.replace("is False", "not ")

        # Aplicar autopep8 para corrigir F401, E712 e outros
        content = autopep8.fix_code(
            content,
            options={
                "ignore": ["E501"],  # ignorar linhas longas
                "aggressive": 2,
            },
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ cleaned: {path}")

    except Exception as e:
        print(f"Erro ao limpar {path}: {e}")


def walk_and_clean():
    for root, _, files in os.walk("src"):
        if should_skip(root):
            continue

        for file in files:
            if file.endswith(".py"):
                clean_file(os.path.join(root, file))


def run_commands():
    print("\n🏃 Executando isort...")
    subprocess.run(["python", "-m", "isort", "src"])

    print("\n🎨 Executando black...")
    subprocess.run(["python", "-m", "black", "src"])

    print("\n🔍 Executando flake8 (para confirmar)...")
    subprocess.run(["python", "-m", "flake8", "src"])


if __name__ == "__main__":
    print("🚀 Iniciando limpeza automática do backend...")
    walk_and_clean()
    run_commands()
    print("\n🎉 Limpeza finalizada!")
