# conftest específico para testes unitários
import os
import sys

# Caminho até a pasta /src
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

# Nada de fixtures async ou banco aqui!
