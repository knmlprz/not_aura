# not_aura

Repozytorium **dokumentacji zespołowej** dla projektu roboczego **not_aura** — zasady pracy z **Git**, **styl kodu** oraz konwencje **ROS 2**.

> **Uwaga:** To repozytorium **nie zawiera kodu węzłów ROS ani paczek do zbudowania**. Tu są wyłącznie wytyczne i szablony. Implementacja (paczki `not_aura_*`, launch, konfiguracja) żyje w osobnym workspace ROS 2, np. `not_aura_ws`.

**Zdalne repo:** `git@github.com:knmlprz/not_aura.git`

---

## Spis treści

- [Cel repozytorium](#cel-repozytorium)
- [Struktura katalogów](#struktura-katalogów)
- [Dokumentacja — szybkie linki](#dokumentacja--szybkie-linki)
- [Stos technologiczny](#stos-technologiczny)
- [Workspace ROS 2 (konwencja)](#workspace-ros-2-konwencja)
- [Szybki start (workspace aplikacyjny)](#szybki-start-workspace-aplikacyjny)
- [Git — skrót zasad](#git--skrót-zasad)
- [Nowa paczka ROS 2 — checklist](#nowa-paczka-ros-2--checklist)
- [Klonowanie i wkład w dokumentację](#klonowanie-i-wkład-w-dokumentację)

---

## Cel repozytorium

Zbiór reguł i praktyk dla zespołu **not_aura**:

| Obszar | Opis |
|--------|------|
| **version_control** | Git, branchowanie (GitFlow), commity, code review |
| **code** | Styl Python / C++ / C#, zasady OOP (SOLID, KISS, DRY, YAGNI) |
| **ros** | Układ paczek ROS 2 Humble, workspace, launch, parametry, szablony |

Szczegółowy przegląd: **[docs/README.md](docs/README.md)**.

---

## Struktura katalogów

```
not_aura/
├── README.md                 # ten plik
└── docs/
    ├── README.md             # spis dokumentacji zespołowej
    ├── version_control/
    │   ├── git_rules.md
    │   ├── branching_strategy.md
    │   ├── commits.md
    │   └── cr.md
    ├── code/
    │   ├── code_style.md
    │   └── object_programming.md
    └── ros/
        ├── ros_wiki.md       # paczki ROS 2
        ├── new_ws.md         # workspace
        ├── ros_readme.md     # szablon README paczki
        └── .ros_gitignore    # szablon .gitignore dla paczek
```

---

## Dokumentacja — szybkie linki

### Kontrola wersji

| Temat | Plik |
|-------|------|
| Zasady Git, submoduły, LFS | [docs/version_control/git_rules.md](docs/version_control/git_rules.md) |
| Strategia branchowania (GitFlow) | [docs/version_control/branching_strategy.md](docs/version_control/branching_strategy.md) |
| Commity (Conventional Commits) | [docs/version_control/commits.md](docs/version_control/commits.md) |
| Code review i merge requesty | [docs/version_control/cr.md](docs/version_control/cr.md) |

### Kod

| Temat | Plik |
|-------|------|
| Styl kodu (Python, C++, C#) | [docs/code/code_style.md](docs/code/code_style.md) |
| Programowanie obiektowe | [docs/code/object_programming.md](docs/code/object_programming.md) |

### ROS 2

| Temat | Plik |
|-------|------|
| Tworzenie i układ paczek | [docs/ros/ros_wiki.md](docs/ros/ros_wiki.md) |
| Organizacja workspace | [docs/ros/new_ws.md](docs/ros/new_ws.md) |
| Szablon README paczki | [docs/ros/ros_readme.md](docs/ros/ros_readme.md) |
| Szablon `.gitignore` | [docs/ros/.ros_gitignore](docs/ros/.ros_gitignore) |

---

## Stos technologiczny

| Warstwa | Wybór zespołu |
|---------|----------------|
| Middleware | **ROS 2 Humble** |
| Build | **colcon** (`--symlink-install`) |
| C++ | **ament_cmake**, C++17, `-Wall -Wextra -Wpedantic`, [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) |
| Python | **ament**, PEP 8, formatter **black** |
| Launch | Preferowane **`*.launch.py`** zamiast XML |
| Parametry | `config/params_<nazwa_paczki>.yaml` |
| Zależności | **rosdep** |
| Dokumentacja kodu | **rosdoc2**, Doxygen (C++), Sphinx (Python) |
| Duże pliki | **git LFS** (np. modele, meshe) |
| Wiele wersji ROS | Osobne branche deweloperskie, np. `humble-dev`, `iron-dev` |

---

## Workspace ROS 2 (konwencja)

Paczki autorskie: prefiks **`not_aura_`**, np. `not_aura_localization`, `not_aura_navigation`.  
Paczki zewnętrzne: **oryginalne nazwy** (łatwiejsze śledzenie źródła).

```
not_aura_ws/
├── README.md
├── build/          # generowane — nie commitować
├── install/
├── log/
└── src/
    ├── actuation/          # aktuatory, napędy
    ├── perception/         # lokalizacja, detekcja, itd.
    ├── planning_control/   # nawigacja, sterowanie
    └── sensors/            # lidar, kamera, IMU, …
```

Podział folderów w `src/` jest **umowny** — dostosuj go do projektu. Szczegóły: [docs/ros/new_ws.md](docs/ros/new_ws.md).

### Układ pojedynczej paczki (skrót)

**C++ (preferowany build: CMake):**

```
<package_name>/
├── config/params_<package_name>.yaml
├── include/<package_name>/
├── launch/<package_name>.launch.py
├── src/
├── CMakeLists.txt
├── package.xml
└── README.md          # wg szablonu docs/ros/ros_readme.md
```

**Python:**

```
<package_name>/
├── config/
├── launch/
├── <package_name>/      # moduły Python
├── scripts/
├── CMakeLists.txt
├── package.xml
└── README.md
```

Pełny opis: [docs/ros/ros_wiki.md](docs/ros/ros_wiki.md).

---

## Szybki start (workspace aplikacyjny)

```bash
# 1. Workspace
mkdir -p ~/not_aura_ws/src && cd ~/not_aura_ws

# 2. Dodaj paczki (clone / submodule) do src/
# git submodule add ... src/perception/not_aura_...

# 3. Zależności systemowe i ROS
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src

# 4. Build
colcon build --symlink-install
source install/setup.bash

# 5. Uruchomienie (przykład)
ros2 launch <package_name> <package_name>.launch.py
ros2 launch <package_name> <package_name>.launch.py param:=wartosc
```

---

## Git — skrót zasad

### Branche

| Branch | Rola |
|--------|------|
| `main` | Produkcja, stabilny kod |
| `develop` | Integracja, bieżący rozwój |
| `feat/<opis>` | Nowa funkcja (z `develop`) |
| `release/<wersja>` | Przygotowanie wydania |
| `hotfix/<opis>` | Pilna poprawka produkcji |

Scalanie funkcji do `develop`: **`git merge --no-ff`**, wymagana akceptacja zespołu.  
Nazwy branchy i commity: **po angielsku**.

### Commity

Format **[Conventional Commits](https://www.conventionalcommits.org/)**, np.:

```text
feat(localization): add AMCL fallback
fix(camera): correct image encoding on OAK
docs(ros): update launch parameters table
```

Więcej: [docs/version_control/commits.md](docs/version_control/commits.md).

### Merge requesty

- Do **`develop`**: test lokalny, review, MR.
- Do **`main`**: test na docelowym sprzęcie, review, MR.

Szczegóły: [docs/version_control/cr.md](docs/version_control/cr.md).

### Submoduły i LFS

```bash
git clone --recurse-submodules git@github.com:knmlprz/not_aura.git
```

Duże assety (modele 3D, mapy): **git LFS** — [docs/version_control/git_rules.md](docs/version_control/git_rules.md).

---

## Nowa paczka ROS 2 — checklist

1. Nazwa z prefiksem `not_aura_` (jeśli paczka autorska).
2. Struktura katalogów wg [ros_wiki.md](docs/ros/ros_wiki.md).
3. Launch w Pythonie: `<package_name>.launch.py`.
4. Parametry: `config/params_<package_name>.yaml`.
5. Skopiuj [.ros_gitignore](docs/ros/.ros_gitignore) do paczki.
6. README paczki z [ros_readme.md](docs/ros/ros_readme.md) — topici, serwisy, instalacja, uruchomienie.
7. Styl kodu: [code_style.md](docs/code/code_style.md).

---

## Klonowanie i wkład w dokumentację

```bash
git clone --recurse-submodules git@github.com:knmlprz/not_aura.git
cd not_aura
```

**Zmiana zasad zespołu:** edytuj odpowiedni plik w `docs/` i zrób MR do `develop` (opis zmiany w commicie: `docs(...): ...`).

**Nowy członek zespołu:** zacznij od [docs/README.md](docs/README.md) → Git → styl kodu → ROS wiki.

---

## Powiązane repozytoria

Kod runtime (węzły, launch, hardware) **nie jest w tym repo**. Szukaj paczek `not_aura_*` w workspace zespołu lub na GitHubie organizacji **knmlprz**.  
Ten repozytorium definiuje **jak** pisać i organizować ten kod — nie **co** aktualnie jest wdrożone na robocie.

---

## Licencja

Plik `LICENSE` nie jest zdefiniowany w tym repozytorium — uzupełnij, jeśli wymagane przez organizację.
