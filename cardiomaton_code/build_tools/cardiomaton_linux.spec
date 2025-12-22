# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None
current_dir = os.getcwd()

a = Analysis(
    ['main_with_front.py'],
    pathex=[current_dir, os.path.join(current_dir, 'src')],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include src directory
        ('resources', 'resources'),  # Include resources directory
    ],
    hiddenimports=[
        # Standard library modules
        'json', 'enum', 'typing', 'collections', 'itertools',
        'math', 'random', 'time', 'datetime', 'os', 'sys',
        
        # Your Cython modules
        'src.backend.enums.cell_state',
        'src.backend.enums.cell_type',
        'src.backend.models.automaton',
        'src.backend.models.frame_recorder',
        'src.backend.services.simulation_service',
        'src.backend.services.simulation_loop',
        'src.backend.services.action_potential_generator',
        'src.backend.structs.c_cell',
        'src.backend.structs.cell_snapshot',
        'src.backend.structs.cell_wrapper',
        'src.backend.utils.charge_update',
        'src.backend.utils.draw_functions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cardiomaton',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,  # Change to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Remove icon for now to simplify
)