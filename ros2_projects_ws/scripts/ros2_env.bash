#!/usr/bin/bash

# Minimal ROS environment loaded in every container shell.

if [[ -n "${_ROS2_PROJECTS_WS_ENV_LOADED:-}" ]]; then
    return
fi
export _ROS2_PROJECTS_WS_ENV_LOADED=1

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS2_PROJECTS_WS_ROOT="$(cd "$script_dir/.." && pwd)"

export ROS_DISTRO="${ROS_DISTRO:-humble}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"

# Prevent stale overlays from a different ROS distro leaking into this shell.
unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH
unset COLCON_PREFIX_PATH

if [ -f "/opt/ros/$ROS_DISTRO/local_setup.bash" ]; then
    source "/opt/ros/$ROS_DISTRO/local_setup.bash"
fi

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="file://$ROS2_PROJECTS_WS_ROOT/scripts/cyclone-dds.xml"

if [ -f "$ROS2_PROJECTS_WS_ROOT/scripts/macros.bash" ]; then
    source "$ROS2_PROJECTS_WS_ROOT/scripts/macros.bash"
fi
