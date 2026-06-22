#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def get_tree(path: Path, prefix: str = "", depth: int = 0, max_depth: int = 5) -> None:
    """Выводит дерево файлов и папок."""
    if depth > max_depth:
        return
    
    try:
        items = sorted([p for p in path.iterdir() if not p.name.startswith('.') and 
                       p.name not in ['__pycache__', 'venv', 'env', '.git', 'node_modules', 
                                     '.idea', '.vscode']],
                      key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return
    
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{item.name}{'/' if item.is_dir() else ''}")
        
        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            get_tree(item, new_prefix, depth + 1, max_depth)

if __name__ == "__main__":
    root = Path.cwd()
    print(f"Структура проекта: {root}\n")
    get_tree(root, max_depth=5)