# not_aura — standardy zespołu

Zbiór **zasad inżynierskich** dla projektu roboczego **not_aura**: Git (GitFlow), pisanie kodu (Python / C++ / C#), OOP oraz paczki **ROS 2 Humble**. Materiał jest w plikach Markdown w `docs/` — poniżej skrót **wyciągnięty z treści tych dokumentów**, nie z „opisu repozytorium”.

Pełne wersje: **[docs/README.md](docs/README.md)**.

---

## Spis treści

1. [Git i wersjonowanie](#git-i-wersjonowanie)
2. [Commity](#commity)
3. [Code review i merge requesty](#code-review-i-merge-requesty)
4. [Styl kodu](#styl-kodu)
5. [Programowanie obiektowe](#programowanie-obiektowe)
6. [ROS 2 — workspace i paczki](#ros-2--workspace-i-paczki)
7. [Szablon README paczki](#szablon-readme-paczki)
8. [Gdzie szukać szczegółów](#gdzie-szukać-szczegółów)

---

## Git i wersjonowanie

### Branche (GitFlow)

| Branch | Rola |
|--------|------|
| `main` | Produkcja — `HEAD` = stan gotowy do wdrożenia |
| `develop` | Integracja — bieżący rozwój pod następne wydanie |
| `feat/<nazwa>` | Nowa funkcja (z `develop`, merge z powrotem do `develop`) |
| `release/<wersja>` | Przygotowanie wydania (np. `release/1.2`) |
| `hotfix/<nazwa>` | Pilna poprawka produkcji |

Przy wielu wersjach ROS 2: osobne branche deweloperskie, np. **`humble-dev`**, **`iron-dev`**.

**Feature — start:**

```bash
git checkout -b feat/name develop
```

**Feature — merge do develop (wymagana akceptacja zespołu):**

```bash
git checkout develop
git merge --no-ff feat/name
git branch -d feat/name
git push origin develop
```

Flaga **`--no-ff`** — zawsze osobny commit merge; zachowana historia gałęzi funkcji.

### Zasady ogólne ([git_rules.md](docs/version_control/git_rules.md))

- Język **angielski**: branche, commity, opisy wydań.
- Prefiksy branchy: `main`, `develop`, `feat/`, `hotfix/`, `release/`.
- Przykład nazwy: `feat/add_navigation_module`.
- Scalanie do `main` łączy się z **release** kodu.

### Submoduły

```bash
git clone --recurse-submodules git@github.com:knmlprz/not_aura.git

git submodule add git@example.com:group/repository.git
git submodule add git@example.com:group/repository.git --branch develop
git submodule add git@example.com:group/repo.git /path/to/clone

git submodule update --init --recursive
git submodule update --remote
git submodule foreach 'git checkout develop'
```

### Git LFS (duże pliki, np. `*.mesh`)

```bash
sudo apt install git-lfs
git lfs track "*.mesh"
# potem add + commit — wpis w .gitattributes
```

---

## Commity

Format **[Conventional Commits](https://www.conventionalcommits.org/)** ([commits.md](docs/version_control/commits.md)):

```text
<type>[optional scope]: <Description starting with capital letter>

[optional body]

[optional footer(s)]
```

| `type` | Znaczenie |
|--------|-----------|
| `feat` | Nowa funkcja |
| `fix` | Naprawa błędu |
| `style` | Styl (bez zmiany logiki) |
| `refactor` | Refaktoryzacja |
| `test` | Testy |
| `docs` | Dokumentacja |
| `chore` | Utrzymanie (np. `.gitignore`) |

**Przykłady z dokumentacji:**

```text
feat(lang): Add Polish language
fix: Prevent racing of requests
docs: Correct spelling of CHANGELOG
feat!: Send an email when a product is shipped
feat(api)!: Send an email when a product is shipped
```

Stopka ze zgłoszeniem: `[TASK-ID]` lub `Refs: #123`.

```bash
git add path/to/file
git commit -m "feat(perception): Add person detector node"
```

---

## Code review i merge requesty

Źródło: [cr.md](docs/version_control/cr.md).

**Recenzja obejmuje:**

- **Nazewnictwo** — angielski, zrozumiałe, adekwatne do roli zmiennej/metody.
- **Komentarze** — tylko potrzebne; brakujące uzupełnić.
- **Funkcjonalność** — prostsze rozwiązania zgłaszać w review; czytelność OOP.
- **Styl** — Python: **black**; reszta: [code_style.md](docs/code/code_style.md).
- **Testy** — build i uruchomienie wg README paczki.
- **Dokumentacja** — aktualne README (szablon), przepływ sygnałów, Doxygen / docstring.

**Merge request — obowiązkowo:**

| Cel merge | Wymaganie |
|-----------|-----------|
| → `develop` | Działa **lokalnie** na komputerze |
| → `main` | Testy na **docelowym urządzeniu** |

- MR możliwy do sensownego przejrzenia (bez „miliona linii”).
- Min. **1 recenzent**, **nie autor**.
- Merge po poprawkach i **co najmniej jednej akceptacji**.
- Tytuł MR: np. `Feature add logging [TASK-ID]`.

---

## Styl kodu

Wspólne dla wszystkich języków ([code_style.md](docs/code/code_style.md)):

1. Zasady OOP — [object_programming.md](docs/code/object_programming.md).
2. **Angielski** — identyfikatory, komentarze, dokumentacja.
3. **Modułowość**.
4. Wcięcie: **4 spacje**.

### Python

- [PEP 8](https://peps.python.org/pep-0008/) + formatter **[black](https://github.com/psf/black)**.
- Pliki: `snake_case.py`.
- Zmienne / funkcje: `snake_case`; klasy: `PascalCase`.
- Prywatne: prefiks `_` (np. `_internal_value`).
- Stałe: `UPPER_SNAKE_CASE`.
- Dokumentacja: **docstring** (PEP 257).

### C++

- **C++17**, [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html).
- Pliki: `snake_case` w `src/` i `include/`.
- Nagłówki: **`#pragma once`**.
- Nawiasy funkcji/klas: **od nowej linii**.
- Zmienne: `snake_case`; prywatne pola klasy: sufiks `_` (np. `table_name_`).
- Stałe: `kMixedCase` (np. `kDaysInAWeek`); `#define` — `UPPER_SNAKE`.
- Klasy / funkcje / metody: **`PascalCase`** (np. `AddTableEntry()`).
- Dokumentacja: **Doxygen** w komentarzach nagłówkowych.

### C#

- [Unity C#](https://blog.unity.com/engine-platform/clean-up-your-code-how-to-create-your-own-c-code-style) + [.NET naming](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names).
- Lokalne: `camelCase`; prywatne pola: `m_` + camelCase; właściwości / metody / klasy: `PascalCase`.
- Interfejsy: prefiks **`I`** (np. `IWorkerQueue`).
- Dokumentacja: **XML comments** → Doxygen.

---

## Programowanie obiektowe

Źródło: [object_programming.md](docs/code/object_programming.md).

| Skrót | Zasada |
|-------|--------|
| **S** | Single responsibility — jedna odpowiedzialność na klasę |
| **O** | Open/closed — rozszerzaj, nie modyfikuj bez potrzeby |
| **L** | Liskov — podklasy nie łamią kontraktu bazy |
| **I** | Interface segregation — małe, dedykowane interfejsy |
| **D** | Dependency inversion — zależność od abstrakcji |
| **KISS** | Prosto, bez zbędnych udziwnień |
| **DRY** | Bez powtórzeń w kodzie i procesie |
| **YAGNI** | Nie implementuj „na zapas” |

---

## ROS 2 — workspace i paczki

Źródło: [new_ws.md](docs/ros/new_ws.md), [ros_wiki.md](docs/ros/ros_wiki.md).

### Workspace

```text
not_aura_ws/
├── build/ install/ log/    # nie commitować
└── src/
    ├── actuation/          # aktuatory
    ├── perception/         # lokalizacja, detekcja, …
    ├── planning_control/   # nawigacja, sterowanie
    └── sensors/            # lidar, kamera, IMU, …
```

- Paczki **autorskie**: prefiks **`not_aura_`** (np. `not_aura_localization`).
- Paczki **zewnętrzne**: oryginalna nazwa upstream.
- Paczki w `src/` — w repo lub jako **git submodule**.

**Build:**

```bash
cd not_aura_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

### Układ paczki C++ (preferowany: `ament_cmake`)

```text
<package_name>/
├── config/params_<package_name>.yaml
├── include/<package_name>/
├── launch/<package_name>.launch.py   # preferowane nad .xml
├── src/
├── CMakeLists.txt
├── package.xml
└── README.md
```

### Układ paczki Python

```text
<package_name>/
├── config/params_<package_name>.yaml
├── launch/<package_name>.launch.py
├── <package_name>/__init__.py
├── scripts/
├── CMakeLists.txt
├── package.xml
└── README.md
```

Przy nowej paczce: skopiuj **[.ros_gitignore](docs/ros/.ros_gitignore)** do katalogu paczki.

### Parametry YAML

Domyślny plik: **`config/params_<package_name>.yaml`**. Struktura ROS 2:

```yaml
node_name:
  ros__parameters:
    bool_value: true
    int_number: 5
```

### Launch

**Preferowany:** `package_name.launch.py`

```bash
ros2 launch package_name package_name.launch.py
ros2 launch package_name package_name.launch.py arg_name:=value
```

Minimalny szkielet (z dokumentacji):

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()
    # DeclareLaunchArgument, Node(package=..., executable=...), ld.add_action(...)
    return ld
```

`.launch.xml` — tylko przy migracji z ROS 1.

### CMake (fragment wymagań)

- `cmake_minimum_required`, `project()`, **C++14+** (w przykładzie; styl C++17 w code_style).
- Flagi: **`-Wall -Wextra -Wpedantic`** (GCC/Clang).
- `find_package(ament_cmake REQUIRED)`, `ament_target_dependencies`, `install`, `ament_package()`.

### Dokumentacja paczek

- **rosdoc2** — generowanie docs workspace.
- C++: Doxygen; Python: Sphinx / docstring.

---

## Szablon README paczki

Każda paczka ma własny `README.md` wg [ros_readme.md](docs/ros/ros_readme.md):

- Project structure  
- Dependencies (subscribers / publishers / services — tabele topiców)  
- Installation (`colcon build --symlink-install`)  
- Parameters  
- Usage (`ros2 launch …`)  
- Class diagram, visuals, roadmap, contributors  

---

## Gdzie szukać szczegółów

| Temat | Plik |
|-------|------|
| Git, submoduły, LFS | [docs/version_control/git_rules.md](docs/version_control/git_rules.md) |
| GitFlow (release, hotfix) | [docs/version_control/branching_strategy.md](docs/version_control/branching_strategy.md) |
| Commity | [docs/version_control/commits.md](docs/version_control/commits.md) |
| Code review | [docs/version_control/cr.md](docs/version_control/cr.md) |
| Styl kodu | [docs/code/code_style.md](docs/code/code_style.md) |
| SOLID, KISS, DRY, YAGNI | [docs/code/object_programming.md](docs/code/object_programming.md) |
| Paczki ROS 2 | [docs/ros/ros_wiki.md](docs/ros/ros_wiki.md) |
| Workspace | [docs/ros/new_ws.md](docs/ros/new_ws.md) |
| Szablon README paczki | [docs/ros/ros_readme.md](docs/ros/ros_readme.md) |

---

## Uwaga o zakresie tego katalogu

W **`/home/rafal/not_aura`** nie ma plików `package.xml`, węzłów ROS ani `CMakeLists.txt` z logiką robota — są **wytyczne zespołu** w Markdown. Implementacja (np. `not_aura_*` w `not_aura_ws`) powstaje w osobnych repozytoriach / submodułach zgodnie z powyższymi regułami.

**Klonowanie dokumentacji:**

```bash
git clone --recurse-submodules git@github.com:knmlprz/not_aura.git
```
