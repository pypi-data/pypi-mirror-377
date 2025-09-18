#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para build e publicação do SearchableDropdown no PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Executa um comando e trata erros"""
    print(f"\n🔄 {description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído com sucesso!")
        if result.stdout:
            print(f"Saída: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {description.lower()}:")
        print(f"Erro: {e.stderr}")
        return False

def clean_build_dirs():
    """Remove diretórios de build antigos"""
    print("\n🧹 Limpando diretórios de build...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                print(f"Removendo: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removendo: {path}")
                path.unlink()

def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    print("\n🔍 Verificando dependências...")
    
    required_packages = ['setuptools', 'wheel', 'twine', 'build']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n⚠️  Instalando dependências faltantes: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        if not run_command(install_cmd, "Instalar dependências"):
            return False
    
    # Verificar configuração do PyPI
    print("\n🔍 Verificando configuração do PyPI...")
    pypirc_path = os.path.expanduser("~/.pypirc")
    if os.path.exists(pypirc_path):
        print(f"✅ Arquivo .pypirc encontrado em: {pypirc_path}")
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(pypirc_path)
            
            if 'pypi' in config:
                print("✅ Configuração PyPI oficial encontrada")
            if 'testpypi' in config:
                print("✅ Configuração TestPyPI encontrada")
                
        except Exception as e:
            print(f"⚠️  Erro ao ler .pypirc: {e}")
    else:
        print(f"⚠️  Arquivo .pypirc não encontrado em: {pypirc_path}")
        print("   Certifique-se de configurar o .pypirc com seus tokens")
    
    return True

def run_tests():
    """Executa os testes antes do build"""
    print("\n🧪 Executando testes...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('recoveredperispirit/django/django_searchable_dropdown/tests'):
        print("❌ Diretório de testes não encontrado. Certifique-se de estar no diretório raiz do projeto.")
        return False
    
    # Executar testes
    test_cmd = "cd recoveredperispirit/django/django_searchable_dropdown && python -m pytest tests/ -v"
    return run_command(test_cmd, "Executar testes")

def build_package():
    """Constrói o pacote"""
    print("\n📦 Construindo pacote...")
    
    # Build com pyproject.toml (PEP 625 compliant)
    build_cmd = "python -m build"
    return run_command(build_cmd, "Construir pacote")

def check_package():
    """Verifica o pacote construído"""
    print("\n🔍 Verificando pacote...")
    
    # Verificar se os arquivos foram criados
    if not os.path.exists('dist'):
        print("❌ Diretório 'dist' não foi criado!")
        return False
    
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("❌ Nenhum arquivo encontrado em 'dist'!")
        return False
    
    print("📁 Arquivos criados:")
    for file in dist_files:
        print(f"  - {file.name}")
    
    # Verificar com twine
    check_cmd = "twine check dist/*"
    return run_command(check_cmd, "Verificar pacote com twine")

def upload_to_test_pypi():
    """Faz upload para TestPyPI"""
    print("\n🚀 Fazendo upload para TestPyPI...")
    
    upload_cmd = "twine upload --repository testpypi dist/*"
    return run_command(upload_cmd, "Upload para TestPyPI")

def upload_to_pypi():
    """Faz upload para PyPI"""
    print("\n🚀 Fazendo upload para PyPI...")
    
    upload_cmd = "twine upload dist/*"
    return run_command(upload_cmd, "Upload para PyPI")

def main():
    """Função principal"""
    print("🚀 Script de Build e Publicação - SearchableDropdown")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('setup.py'):
        print("❌ Arquivo setup.py não encontrado. Certifique-se de estar no diretório raiz do projeto.")
        sys.exit(1)
    
    # Limpar builds antigos
    clean_build_dirs()
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha ao verificar/instalar dependências.")
        sys.exit(1)
    
    # Executar testes
    if not run_tests():
        print("❌ Testes falharam. Abortando build.")
        sys.exit(1)
    
    # Construir pacote
    if not build_package():
        print("❌ Falha ao construir pacote.")
        sys.exit(1)
    
    # Verificar pacote
    if not check_package():
        print("❌ Falha ao verificar pacote.")
        sys.exit(1)
    
    print("\n🎉 Build concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Para testar no TestPyPI:")
    print("   python build_and_publish.py --test")
    print("2. Para publicar no PyPI:")
    print("   python build_and_publish.py --publish")
    print("3. Para apenas fazer o build:")
    print("   python build_and_publish.py --build-only")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            main()
            if upload_to_test_pypi():
                print("\n✅ Upload para TestPyPI concluído!")
                print("🔗 Teste a instalação com: pip install --index-url https://test.pypi.org/simple/ django-searchable-dropdown")
            else:
                print("\n❌ Falha no upload para TestPyPI.")
        elif sys.argv[1] == "--publish":
            main()
            if upload_to_pypi():
                print("\n✅ Upload para PyPI concluído!")
                print("🔗 Pacote disponível em: https://pypi.org/project/django-searchable-dropdown/")
            else:
                print("\n❌ Falha no upload para PyPI.")
        elif sys.argv[1] == "--build-only":
            main()
        else:
            print("❌ Opção inválida. Use --test, --publish ou --build-only")
    else:
        main()
