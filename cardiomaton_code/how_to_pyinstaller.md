# Budowanie aplikacji Cardiomaton z użyciem PyInstaller


---

## 1. Wstępna budowa aplikacji

Uruchom aplikację tak jak normalnie czyli przy użyciu cardiomaton.bat na Windowsie lub cardiomaton.sh na Linuxie lub macOS.

## 2. Zaaktualizuj poetry

W toml pojawiło się

``` pyinstaller = { version = "^6.17.0", markers = "python_version < '3.15'" } ```

więc 

```
poetry lock
poetry install
```

## 3. Pyinstaller specyfikacja

W tym samym katalogu co main_with_front.py utwórz plik .spec i wklej (w .gitignore jest dodany .spec, a wolę juz go nie modyfikować więc wstawiam tu):
```
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

# Główny plik
main_script = 'main_with_front.py'

# Katalog projektu (root)
project_dir = os.getcwd()

# Katalog z kodem źródłowym
src_dir = os.path.join(project_dir, 'src')

# Katalog z zasobami
resources_dir = os.path.join(project_dir, 'resources')

# Zbieramy wszystkie podmoduły z src/, aby uniknąć problemów z dynamicznym importem
hiddenimports = collect_submodules('src') + [

    # enums
    "src.backend.enums.cell_state",
    "src.backend.enums.cell_type",

    # models
    "src.backend.models.automaton",
    "src.backend.models.frame_recorder",

    # services
    "src.backend.services.simulation_service",
    "src.backend.services.simulation_loop",
    "src.backend.services.action_potential_generator",

    # structs
    "src.backend.structs.c_cell",
    "src.backend.structs.cell_snapshot",
    "src.backend.structs.cell_wrapper",

    # utils
    "src.backend.utils.charge_update",
    "src.backend.utils.draw_functions",
]


# ANALYSIS
a = Analysis(
    [main_script],
    pathex=[project_dir, src_dir],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

# PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ikona aplikacji
icon_img = os.path.join(resources_dir, 'icon')

# .ico - windows | .png - linux | .icns macOS
icon_img = os.path.join(icon_img, 'logo.ico')


# EXE – okienkowy tryb (PyQt)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cardiomaton',
    icon=icon_img,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # PyQt => brak konsoli
    disable_windowed_traceback=False,
)
# COLLECT – wersja one-folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='Cardiomaton'
)

```

Podmień rozszerzenie obrazu ikony w zależnosci od OS:
```python
# .ico - windows | .png - linux | .icns macOS
icon_img = os.path.join(icon_img, 'logo.ico')
```

## 4. Resources

Resources nie są uwzględniane przy tworzeniu paczki ( jak je wcześniej uwzględniałem to i tak nie działało :-( ).
Po poprawnym zbudowaniu skopuj katalog resources z projektu (Cardiomaton_code/cardiomaton_code/resources) do folderu utworzonego przez pyinstaller w którym znajduje się plik wykonywalny (do katalogu dist).

## 5. Koniec

Powinno się uruchomić, ale nie zdziwię się jak pojawią się problemy z nieznajdowaniem zasobów lub ogólnie z katalogami. Jeśli wystąpią problemy to należy je rozwiązać. Dziękuję.