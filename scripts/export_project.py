#!/usr/bin/env python3
"""
THIN — Script de Exportação e Empacotamento de Portabilidade
Gera:
1. Pasta descompactada: thin-site-export/
2. Arquivo ZIP portátil do código-fonte: thin-site-export.zip (e THIN-projeto-completo.zip)
3. Arquivo ZIP pronto para publicação estática: THIN-site-producao-dist.zip
4. Sincronização em public/downloads/ e dist/downloads/ para download direto via navegador
"""

import os
import zipfile
import shutil
from pathlib import Path

ROOT_DIR = Path('/app/applet')
EXPORT_DIR = ROOT_DIR / 'thin-site-export'
DIST_DIR = ROOT_DIR / 'dist'
PUBLIC_DOWNLOADS = ROOT_DIR / 'public' / 'downloads'
DIST_DOWNLOADS = DIST_DIR / 'downloads'

# Cria diretórios de download
PUBLIC_DOWNLOADS.mkdir(parents=True, exist_ok=True)
DIST_DOWNLOADS.mkdir(parents=True, exist_ok=True)

# 1. Preparar a pasta organizada 'thin-site-export'
if EXPORT_DIR.exists():
    shutil.rmtree(EXPORT_DIR)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Arquivos raiz a copiar
ROOT_FILES = [
    'index.html',
    'package.json',
    'package-lock.json',
    'vite.config.ts',
    'tsconfig.json',
    'netlify.toml',
    'vercel.json',
    '.env.example',
    '.gitignore',
    'GUARDIAN.md',
    'README.md',
]

for fname in ROOT_FILES:
    src_f = ROOT_DIR / fname
    if src_f.exists():
        shutil.copy2(src_f, EXPORT_DIR / fname)

# Pastas a copiar
DIRS_TO_COPY = ['src', 'scripts']
for dname in DIRS_TO_COPY:
    src_d = ROOT_DIR / dname
    if src_d.exists():
        shutil.copytree(src_d, EXPORT_DIR / dname, dirs_exist_ok=True)

# Pasta public (copiar assets essenciais, excluindo temporários do aistudio e zips)
public_dest = EXPORT_DIR / 'public'
public_dest.mkdir(parents=True, exist_ok=True)

for item in (ROOT_DIR / 'public').iterdir():
    if item.name in ('downloads', 'assets'):
        continue
    if item.is_file():
        shutil.copy2(item, public_dest / item.name)

# Copiar assets limpos (apenas os assets de produção)
assets_src = ROOT_DIR / 'public' / 'assets'
assets_dest = public_dest / 'assets'
assets_dest.mkdir(parents=True, exist_ok=True)

for asset in assets_src.iterdir():
    if asset.is_file() and not asset.name.endswith('.zip'):
        shutil.copy2(asset, assets_dest / asset.name)

# Copiar workflows do GitHub Actions
gh_src = ROOT_DIR / '.github'
if gh_src.exists():
    shutil.copytree(gh_src, EXPORT_DIR / '.github', dirs_exist_ok=True)

print(f"Pasta organizada criada em: {EXPORT_DIR}")

# 2. Gerar thin-site-export.zip (código-fonte completo e limpo)
export_zip_path = ROOT_DIR / 'thin-site-export.zip'
print(f"Criando {export_zip_path}...")
with zipfile.ZipFile(export_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(EXPORT_DIR):
        for file in sorted(files):
            full_path = Path(root) / file
            rel_path = full_path.relative_to(EXPORT_DIR)
            # Adiciona com prefixo de pasta limpa
            archive_name = Path('thin-site-export') / rel_path
            zf.write(full_path, str(archive_name))

print(f"thin-site-export.zip gerado com sucesso ({export_zip_path.stat().st_size:,} bytes).")

# 3. Gerar THIN-site-producao-dist.zip (arquivos compilados prontos para deploy direto)
dist_zip_path = ROOT_DIR / 'THIN-site-producao-dist.zip'
print(f"Criando {dist_zip_path}...")
with zipfile.ZipFile(dist_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(DIST_DIR):
        dirs[:] = [d for d in dirs if d not in ('downloads', 'aistudio')]
        for file in sorted(files):
            full_path = Path(root) / file
            rel_path = full_path.relative_to(DIST_DIR)
            zf.write(full_path, str(rel_path))

print(f"THIN-site-producao-dist.zip gerado com sucesso ({dist_zip_path.stat().st_size:,} bytes).")

# 4. Manter THIN-projeto-completo.zip como cópia idêntica de thin-site-export.zip
full_zip_path = ROOT_DIR / 'THIN-projeto-completo.zip'
shutil.copy2(export_zip_path, full_zip_path)

# 5. Sincronizar os zips nas pastas públicas para download via HTTP
for zpath in [export_zip_path, dist_zip_path, full_zip_path]:
    shutil.copy2(zpath, PUBLIC_DOWNLOADS / zpath.name)
    shutil.copy2(zpath, DIST_DOWNLOADS / zpath.name)

print("Todos os pacotes ZIP foram copiados para public/downloads/ e dist/downloads/ com sucesso.")
