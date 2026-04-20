# Workspace w ROS2

Spis treści

- [Workspace w ROS2](#workspace-w-ros2)
  - [Wprowadzenie](#wprowadzenie)
  - [Struktura](#struktura)
  - [Budowanie](#budowanie)



## Wprowadzenie

Projekty ROS2 działają na bazie przestrzeni roboczej (workspace), która umożliwia budowanie znajdujących się w nim paczek. W ramach folderu `src` znajdują się paczki tworzone zgodnie z założeniami ROS2. W folderze `install` znajdują się stworzone pliki instalacyjne, w folderze `build` pliki z budowy projektu, a folder `logs` zawiera logi ROS2 z uruchomień.

Zostało przyjęte założenie, że tworzone paczki nazywane są akronimem nazwy projektu, którego dotyczą np. `not_aura_ws`, `not_aura_localization`, w przypadku paczek autorskich. Z kolei paczki wykorzystywane w ramach projektu, nie stworzone przez zespół, pozostają z ich oryginalnym nazewnictwem w celu łatwiejszej identyfikacji źródła pochodzenia paczki.

Paczki dodawane do projektu w folderze `src` mogą być utrzymywane zarówno bezpośrednio w tym repozytorium, jak i (opcjonalnie) w formie [submodułów git](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), jeśli zespół chce rozdzielić je na osobne repozytoria.

## Struktura

Struktura przestrzeni roboczej projektu może się różnić w zależności od realizowanego projektu. W celu rozgraniczenia logiki projektu tworzonych jest zwykle kilka podstawowych folderów grupujących stworzone paczki.

```shell
├── README.md
├── install     # dirs exist after build  
├── build       # and not pushing to
├── log         # katalog logów ROS2 (np. po build/run)
└── src
    ├── actuation
    │   └── <project_name>_actuators_pkg
    ├── perception
    │   └── <project_name>_localization_pkg
    ├── planning_control
    │   └── <project_name>_navigation_pkg
    └── sensors
        ├── lidar_pkg
        └── camera_pkg
```

W przypadku projektów opartych na rzeczywistym robocie przyjęte zostały grupy podziału, które uporządkowują logicznie poszczególne moduły kodu. Podział ten wygląda następująco:

- `actuation` - paczki odpowiadające za elementy wykonawcze urządzenia np. komunikację z aktuatorami,
- `perception` - paczki dotyczące szeroko pojętej percepcji robota, np. rozpoznawania, identyfikacji obiektów, lokalizacji itp.,
- `planning_control` - moduły odpowiadające za sterowania i planowanie ruchu,
- `sensors` - paczki odpowiedzialne za komunikację z czujnikami np. kamery, lidary, czujniki inercji itp.

Poniżej schemat przykładowego projektu podzielonego według powyższych grup.
Project structure example

Przyjęty podział jest umowny i zależy od realizowanego projektu, w związku z tym można go zmienić w zależności od potrzeby.

## Budowanie

W celu zbudowania przestrzeni roboczej w ROS2 wykorzystywany jest [colcon](https://colcon.readthedocs.io/en/released/user/quick-start.html), o którym więcej informacji można znaleźć w [dokumentacji ROS2](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html#install-colcon).

Żeby zbudować przykładowy projekt należy przejść do głównego folderu projektu, a następnie użyć komendy

```bash
colcon build --symlink-install
```

Flaga `--symlink-install` pozwala na zbudowanie projektu z odnośnikami do odpowiednich plików, umożliwiając edytowanie plików bez konieczności ich ponownego budowania.