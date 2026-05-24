# ROS2 Projects Workspace

Minimal ROS 2 workspace tooling with:

- one launcher: `./scripts/distrobox <humble|jazzy>`
- one env file loaded automatically in container shells
- one build macro: `build`

## Prerequisites

- [Docker](https://www.docker.com) or [Podman](https://podman.io)
- [Distrobox](https://github.com/89luca89/distrobox)
- `rosdep`, `colcon`, `python3-pip` available in container image

## Start Container

Run one of:

```bash
./scripts/distrobox humble
./scripts/distrobox jazzy
```

What this does:

- creates/enters distro-specific container (`ros2_projects_ws_<distro>`)
- appends env hook to container `~/.bashrc` (idempotent)
- auto-loads `scripts/ros2_env.bash` in every new terminal inside container

`ros2_env.bash` sets:

- `ROS_DISTRO`
- `ROS_DOMAIN_ID` (default `0`, unless already set)
- `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`
- `CYCLONEDDS_URI=file://.../scripts/cyclone-dds.xml`
- source `/opt/ros/$ROS_DISTRO/local_setup.bash`
- source `scripts/macros.bash` (contains `build`)

## Build Macro

`build` is the only macro and runs in the **current working directory**.

Requirements for `build`:

- current directory must contain `./src`
- ROS packages are discovered from `./src`

What `build` does:

1. `rosdep install --from-paths ./src ...`
2. installs extra apt dependencies from `apt_packages.txt` in package folders
3. installs extra pip dependencies from `requirements.txt` in package folders
4. runs `colcon build --base-paths ./src`
5. uses distro-scoped artifacts:
  - `build_<ROS_DISTRO>`
  - `install_<ROS_DISTRO>`
  - `log_<ROS_DISTRO>`

Examples:

```bash
# Build all packages found in ./src
build

# Build selected packages (exact colcon package names)
build my_pkg another_pkg
```

## Diagnostic Macro

Use `diag` to quickly print system info and validate environment from `scripts/ros2_env.bash`:

```bash
diag
```

It checks:

- ROS/Cyclone variables are present
- `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`
- `CYCLONEDDS_URI` points to workspace `scripts/cyclone-dds.xml`
- env load marker (`_ROS2_PROJECTS_WS_ENV_LOADED`) is set

## Project Structure

```yaml
scripts/
  distrobox
  ros2_env.bash
  macros.bash
  cyclone-dds.xml
src/
```

