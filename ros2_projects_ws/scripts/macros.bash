#!/usr/bin/bash

build() {
    if [ ! -d "./src" ]; then
        echo "Missing ./src in current directory: $(pwd)"
        return 1
    fi

    local ros_distro_name="${ROS_DISTRO:-humble}"
    local build_base="build_${ros_distro_name}"
    local install_base="install_${ros_distro_name}"
    local log_base="log_${ros_distro_name}"

    echo "Updating rosdep index..."
    rosdep update --rosdistro "$ros_distro_name"

    echo "Installing rosdep dependencies..."
    rosdep install --rosdistro "$ros_distro_name" --default-yes --ignore-packages-from-source --from-paths ./src

    echo "Installing additional APT dependencies..."
    while IFS= read -r apt_file; do
        [ -n "$apt_file" ] || continue
        while IFS= read -r apt_pkg; do
            apt_pkg="$(echo "$apt_pkg" | sed 's/\s*#.*$//g' | xargs)"
            [ -n "$apt_pkg" ] || continue
            sudo apt-get install -y "$apt_pkg"
        done < "$apt_file"
    done < <(find ./src -type f -name apt_packages.txt)

    echo "Installing additional PIP dependencies..."
    while IFS= read -r req_file; do
        [ -n "$req_file" ] || continue
        python3 -m pip install -r "$req_file"
    done < <(find ./src -type f -name requirements.txt)

    echo "Building packages..."
    local colcon_args=(
        "--log-base" "$log_base"
        "build"
        "--base-paths" "./src"
        "--build-base" "$build_base"
        "--install-base" "$install_base"
        "--symlink-install"
    )

    if [ "$#" -gt 0 ]; then
        colcon_args+=("--packages-select" "$@")
    fi

    colcon "${colcon_args[@]}"

    if [ -f "./${install_base}/local_setup.bash" ]; then
        # colcon local_setup can reference COLCON_CURRENT_PREFIX while bootstrapping.
        # Avoid crashing interactive shells if nounset is enabled externally.
        local had_nounset=0
        if [[ $- == *u* ]]; then
            had_nounset=1
            set +u
        fi
        source "./${install_base}/local_setup.bash"
        if [ "$had_nounset" -eq 1 ]; then
            set -u
        fi
    fi

    echo "Done."
}

diag() {
    echo "=== System ==="
    if command -v lsb_release >/dev/null 2>&1; then
        lsb_release -a 2>/dev/null || true
    elif [ -f /etc/os-release ]; then
        cat /etc/os-release
    else
        echo "No lsb_release or /etc/os-release available."
    fi
    echo "Kernel: $(uname -srmo)"
    echo

    echo "=== Tools ==="
    command -v ros2 >/dev/null 2>&1 && echo "ros2: $(command -v ros2)" || echo "ros2: not found"
    command -v colcon >/dev/null 2>&1 && echo "colcon: $(command -v colcon)" || echo "colcon: not found"
    command -v rosdep >/dev/null 2>&1 && echo "rosdep: $(command -v rosdep)" || echo "rosdep: not found"
    echo

    echo "=== Environment ==="
    echo "ROS2_PROJECTS_WS_ROOT=${ROS2_PROJECTS_WS_ROOT:-<unset>}"
    echo "ROS_DISTRO=${ROS_DISTRO:-<unset>}"
    echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-<unset>}"
    echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-<unset>}"
    echo "CYCLONEDDS_URI=${CYCLONEDDS_URI:-<unset>}"
    echo "_ROS2_PROJECTS_WS_ENV_LOADED=${_ROS2_PROJECTS_WS_ENV_LOADED:-<unset>}"
    echo

    echo "=== Checks (ros2_env.bash) ==="
    local ok=true
    local expected_rmw="rmw_cyclonedds_cpp"
    local expected_cyclone_uri=""
    if [ -n "${ROS2_PROJECTS_WS_ROOT:-}" ]; then
        expected_cyclone_uri="file://${ROS2_PROJECTS_WS_ROOT}/scripts/cyclone-dds.xml"
    fi

    if [ "${RMW_IMPLEMENTATION:-}" = "$expected_rmw" ]; then
        echo "[OK] RMW_IMPLEMENTATION is $expected_rmw"
    else
        echo "[FAIL] RMW_IMPLEMENTATION should be $expected_rmw"
        ok=false
    fi

    if [ -n "$expected_cyclone_uri" ] && [ "${CYCLONEDDS_URI:-}" = "$expected_cyclone_uri" ]; then
        echo "[OK] CYCLONEDDS_URI matches workspace path"
    else
        echo "[FAIL] CYCLONEDDS_URI does not match expected workspace path"
        ok=false
    fi

    if [ -n "${ROS2_PROJECTS_WS_ROOT:-}" ] && [ -f "${ROS2_PROJECTS_WS_ROOT}/scripts/cyclone-dds.xml" ]; then
        echo "[OK] cyclone-dds.xml exists"
    else
        echo "[FAIL] cyclone-dds.xml missing"
        ok=false
    fi

    if [ "${_ROS2_PROJECTS_WS_ENV_LOADED:-}" = "1" ]; then
        echo "[OK] ros2_env.bash load marker is set"
    else
        echo "[FAIL] ros2_env.bash load marker is not set"
        ok=false
    fi

    if [ "$ok" = true ]; then
        echo
        echo "Diagnostic status: OK"
    else
        echo
        echo "Diagnostic status: FAIL"
        return 1
    fi
}
