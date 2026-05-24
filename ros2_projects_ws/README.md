# ros2_projects_ws

Minimalny **workspace ROS 2** z gotowym środowiskiem developerskim: kontener **Distrobox**, **CycloneDDS**, makro **`build`** i **`diag`**.  
Katalog **`src/`** służy do paczek ROS (własnych lub podlinkowanych / submodułów). Artefakty buildu są rozdzielone per dystrybucja: `build_humble`, `install_humble`, `log_humble` (analogicznie dla `jazzy`).

Powiązany projekt aplikacyjny (G1, XREAL, teleop, wirtualna kamera): **`~/Web_Speech_remote_control`** (dostosuj ścieżkę do swojego klonu).

---

## Spis treści

- [Struktura katalogów](#struktura-katalogów)
- [Wymagania](#wymagania)
- [Start kontenera (Distrobox)](#start-kontenera-distrobox)
- [Środowisko ROS w kontenerze](#środowisko-ros-w-kontenerze)
- [Budowanie paczek (`build`)](#budowanie-paczek-build)
- [Diagnostyka (`diag`)](#diagnostyka-diag)
- [Gdzie trzymać kod ROS](#gdzie-trzymać-kod-ros)
- [Uruchamianie — G1 + teleop + wirtualna kamera](#uruchamianie--g1--teleop--wirtualna-kamera)
- [Serwisy po starcie bringupu (G1)](#serwisy-po-starcie-bringupu-g1)
- [teleop_moving_window — węzły AR / kamery](#teleop_moving_window--węzły-ar--kamery)
- [Podgląd obrazów](#podgląd-obrazów)

---

## Struktura katalogów

```text
ros2_projects_ws/
├── README.md
├── scripts/
│   ├── distrobox          # wejście do kontenera (humble | jazzy)
│   ├── ros2_env.bash        # ROS_DISTRO, CycloneDDS, source /opt/ros, makra
│   ├── macros.bash          # build, diag
│   └── cyclone-dds.xml      # konfiguracja DDS
├── src/                     # paczki ROS (package.xml w podkatalogach)
├── build_<distro>/          # generowane przez colcon
├── install_<distro>/
└── log_<distro>/
```

---

## Wymagania

Na hoście:

- [Docker](https://www.docker.com) lub [Podman](https://podman.io)
- [Distrobox](https://github.com/89luca89/distrobox)

W obrazie kontenera (instalowane przy tworzeniu / przez `build`):

- ROS 2 **Humble** lub **Jazzy** (wybór przy `./scripts/distrobox`)
- `rosdep`, `colcon`, `python3-pip`

---

## Start kontenera (Distrobox)

Z katalogu `ros2_projects_ws`:

```bash
./scripts/distrobox humble
# lub
./scripts/distrobox jazzy
```

Skrypt:

- tworzy / wchodzi do kontenera `ros2_projects_ws_<distro>`,
- montuje workspace,
- **jednorazowo** dopisuje do `~/.bashrc` w kontenerze hook ładujący `scripts/ros2_env.bash`,
- otwiera interaktywną powłokę bash.

Opcjonalnie: własny obraz Docker — zmienna `ROS_DOCKER_IMAGE` przed uruchomieniem skryptu.

---

## Środowisko ROS w kontenerze

Plik `scripts/ros2_env.bash` ustawia (w każdej nowej powłoce w kontenerze):

| Zmienna / plik | Wartość |
|----------------|---------|
| `ROS_DISTRO` | `humble` lub `jazzy` |
| `ROS_DOMAIN_ID` | domyślnie `0` (jeśli nie ustawione na hoście) |
| `RMW_IMPLEMENTATION` | `rmw_cyclonedds_cpp` |
| `CYCLONEDDS_URI` | `file://.../scripts/cyclone-dds.xml` |
| `ROS2_PROJECTS_WS_ROOT` | katalog główny workspace |

Źródła: `/opt/ros/$ROS_DISTRO/local_setup.bash` oraz `scripts/macros.bash` (`build`, `diag`).

```bash
export ROS_DOMAIN_ID=0   # ten sam ID na wszystkich maszynach w sieci ROS
```

---

## Budowanie paczek (`build`)

Makro **`build`** działa w **bieżącym katalogu**, który musi zawierać `./src`.

Kroki:

1. `rosdep install` z `./src`
2. APT z plików `apt_packages.txt` w paczkach
3. pip z plików `requirements.txt` w paczkach
4. `colcon build --base-paths ./src --symlink-install`
5. artefakty w `build_$ROS_DISTRO`, `install_$ROS_DISTRO`, `log_$ROS_DISTRO`
6. automatyczne `source install_*/local_setup.bash`

```bash
cd /path/to/workspace/with/src

# wszystkie paczki w src/
build

# wybrane paczki (nazwy colcon)
build teleop_moving_window teleop_bringup
```

---

## Diagnostyka (`diag`)

```bash
diag
```

Sprawdza m.in.: `ROS_DISTRO`, `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, `CYCLONEDDS_URI`, marker `_ROS2_PROJECTS_WS_ENV_LOADED`.

---

## Gdzie trzymać kod ROS

Ten workspace **nie zawiera** logiki robota — dostarcza **narzędzia build/run**.

Typowy układ z **Web_Speech_remote_control**:

```bash
# przykład: symlink paczek do src/ (w kontenerze lub na hoście)
cd ~/not_aura/ros2_projects_ws/src
ln -s ~/Web_Speech_remote_control/teleop_ws/src/teleop_moving_window .
ln -s ~/Web_Speech_remote_control/teleop_ws/src/teleop_bringup .
# … pozostałe paczki z teleop_ws/src według potrzeb

cd ~/not_aura/ros2_projects_ws
build teleop_moving_window teleop_bringup
source install_humble/setup.bash
```

Alternatywa: budować bezpośrednio w `~/Web_Speech_remote_control/teleop_ws` (colcon klasyczny) i tylko **`source`** overlay z tego workspace — ważne, żeby **`ROS_DOMAIN_ID`** i **RMW** były spójne.

---

## Uruchamianie — G1 + teleop + wirtualna kamera

Poniżej **połączony** przepływ z `Web_Speech_remote_control/README_g1.md` (bringup G1, XREAL, OAK) oraz `teleop_ws/src/teleop_moving_window/README.md` (wirtualna kamera IMU, detekcja ludzi, streamy).

### 1. Przygotowanie środowiska

```bash
# kontener ROS (zalecane)
cd ~/not_aura/ros2_projects_ws
./scripts/distrobox humble

# w kontenerze — build teleop (ścieżka do Twojego klonu)
cd ~/Web_Speech_remote_control/teleop_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select teleop_moving_window teleop_bringup teleop_hand_eye_tracking teleop_xreal_oak
source install/setup.bash

export ROS_DOMAIN_ID=0
```

### 2. Bringup G1 (RViz, OAK, węzły — funkcje domyślnie wyłączone)

**Symulacja** (bez fizycznego robota):

```bash
ros2 launch teleop_bringup g1_arm_control.launch.py \
  interface:=wlp4s0 \
  publish_joint_states:=false \
  use_robot:=false
```

**Prawy robot**:

```bash
ros2 launch teleop_bringup g1_arm_control.launch.py \
  interface:=eno1 \
  publish_joint_states:=true \
  use_robot:=true
```

Po starcie działają m.in. RViz (model G1 + kamera OAK), ale **śledzenie rąk, IMU XREAL i tułów** wymagają włączenia serwisami (sekcja niżej).

### 3. Wirtualna kamera IMU (gogle XREAL) — osobny terminal

Wymaga **włączonego IMU** (`/xreal/imu/data`) — patrz serwis `enable_imu`.

```bash
source ~/Web_Speech_remote_control/teleop_ws/install/setup.bash
export ROS_DOMAIN_ID=0

# obraz z kamery OAK na „ekranie” w scenie 3D
python3 ~/Web_Speech_remote_control/teleop_ws/src/teleop_moving_window/imu_virtual_camera.py \
  --ros-args -r /laptop/camera/image_raw:=/oak/rgb/image_raw
```

Opcjonalnie — **wyczyść domyślne kostki** w scenie (zostają tylko markery z detektora ludzi):

```bash
ros2 service call /xreal/virtual_camera/clear_all_blocks std_srvs/srv/Trigger
```

Czarne tło:

```bash
ros2 service call /xreal/virtual_camera/set_black_background std_srvs/srv/SetBool "{data: true}"
```

### 4. Detekcja ludzi + czerwone markery w scenie AR — osobny terminal

```bash
source ~/Web_Speech_remote_control/teleop_ws/install/setup.bash
export ROS_DOMAIN_ID=0

python3 ~/Web_Speech_remote_control/teleop_ws/src/teleop_moving_window/people_tracker_node.py
```

Publikuje m.in. `/person/nearest`, `/person/count`, oraz markery na `/xreal/virtual_scene/add_block` (czerwone kostki nad wykrytymi osobami, pozycja z IMU + głębia OAK).

### 5. Stream kamery laptopa (jeśli nie używasz OAK na ekranie wirtualnym)

```bash
python3 ~/Web_Speech_remote_control/teleop_ws/src/teleop_moving_window/laptop_camera_stream_node.py
# topic: /laptop/camera/image_raw
```

### 6. Stream pulpitu (C++, niskie opóźnienie)

Po `colcon build` paczki `teleop_moving_window`:

```bash
source ~/Web_Speech_remote_control/teleop_ws/install/setup.bash
ros2 run teleop_moving_window desktop_screen_stream_node
# domyślnie: /desktop/screen/image_raw
```

Przykład — monitor wirtualny **vkms**:

```bash
sudo modprobe vkms
xrandr --output Virtual-2-1 --mode 1920x1080 --left-of eDP

ros2 run teleop_moving_window desktop_screen_stream_node --ros-args \
  -p monitor_name:=Virtual-2-1 \
  -p primary_monitor_only:=true \
  -p prefer_internal_monitor:=false \
  -p fps:=60.0
```

---

## Serwisy po starcie bringupu (G1)

Źródło: `Web_Speech_remote_control/README_g1.md`. Kolejność włączania dowolna; dla tułowia sensowne: najpierw IMU, potem head→torso.

```bash
# Ręce: mapowanie /hand/* → /g1pilot/hand_goal/*
ros2 service call /hand_tracker_to_arm_goal/set_enabled std_srvs/srv/SetBool "{data: true}"

# IMU z okularów XREAL → /xreal/imu/data
ros2 service call /enable_imu std_srvs/srv/SetBool "{data: true}"

# Tułów według orientacji głowy (wymaga IMU)
ros2 service call /enable_head_to_torso std_srvs/srv/SetBool "{data: true}"
```

Kalibracja żyroskopu IMU (przed pierwszym użyciem):

```bash
ros2 launch teleop_xreal_oak xreal_imu_calib.launch.py
```

Wyłączenie: te same serwisy z `{data: false}`.

---

## teleop_moving_window — węzły AR / kamery

| Komponent | Plik / executable | Główne topici |
|-----------|-------------------|---------------|
| Wirtualna kamera IMU | `imu_virtual_camera.py` | pub: `/xreal/camera/image_raw`, `/xreal/virtual_scene/markers`; sub: `/xreal/imu/data`, `/laptop/camera/image_raw`, `/xreal/virtual_scene/add_block` |
| Detekcja ludzi (YOLO + depth) | `people_tracker_node.py` | pub: `/person/*`, markery sceny |
| Stream laptopa | `laptop_camera_stream_node.py` | pub: `/laptop/camera/image_raw` |
| Stream desktopu | `desktop_screen_stream_node` | pub: `/desktop/screen/image_raw` |
| Viewer desktopu | `desktop_screen_viewer_node` | sub: obraz z topicu |
| Okno X11 pomocnicze | `virtual_display_window_node` | (nie jest monitorem systemowym) |

Build paczki:

```bash
cd ~/Web_Speech_remote_control/teleop_ws
colcon build --packages-select teleop_moving_window
source install/setup.bash
```

Zależności APT (m.in. OpenCV): `teleop_moving_window/apt_packages.txt` — instalowane także przez makro `build`, jeśli paczka leży w `./src`.

Szczegóły parametrów, serwisów i `add_block`:  
`Web_Speech_remote_control/teleop_ws/src/teleop_moving_window/README.md`.

---

## Podgląd obrazów

```bash
ros2 run rqt_image_view rqt_image_view
```

Typowe topici:

- `/xreal/camera/image_raw` — wirtualna kamera (gogle)
- `/oak/rgb/image_raw` — kamera OAK
- `/desktop/screen/image_raw` — pulpit
- `/laptop/camera/image_raw` — kamera laptopa

Lżejszy viewer (C++):

```bash
source ~/Web_Speech_remote_control/teleop_ws/install/setup.bash
ros2 run teleop_moving_window desktop_screen_viewer_node --ros-args \
  -p image_topic:=/xreal/camera/image_raw \
  -p display_fps:=60.0 \
  -p fullscreen:=true
```

---

## RViz (G1 + OAK)

Z `Web_Speech_remote_control/README_g1.md`:

- Fixed Frame: `pelvis`
- Robot G1: **RobotModel**, Description Topic `/robot_description`
- Kamera OAK (opcjonalnie drugi RobotModel): Description Topic `/oak/robot_description`

---

## Powiązane dokumenty

| Dokument | Zawartość |
|----------|-----------|
| [../docs/README.md](../docs/README.md) | Standardy zespołu not_aura (Git, styl, ROS) |
| `~/Web_Speech_remote_control/README_g1.md` | Bringup G1, serwisy, pilot |
| `~/Web_Speech_remote_control/teleop_ws/src/teleop_moving_window/README.md` | Wirtualna kamera, streamy, markery |
