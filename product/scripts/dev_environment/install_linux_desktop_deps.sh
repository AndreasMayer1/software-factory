#!/usr/bin/env bash
# Install Linux desktop runtime dependencies required to run Flutter Linux
# integration tests headlessly inside the devcontainer (REQ-PROC-054 AC-06).
#
# Idempotent: safe to re-run; apt-get install will skip already-installed
# packages.
#
# Usage:
#     bash scripts/dev_environment/install_linux_desktop_deps.sh
#
# Exit codes:
#     0  all packages installed (or already present)
#     1  apt-get failure
#
# Invoked by the devcontainer's postCreateCommand (see
# requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/wsl_devcontainer_setup.md).

set -euo pipefail

# Packages required at runtime by a Flutter Linux desktop binary plus the
# headless framebuffer used by the integration-test gate.
#
#   clang             C/C++ compiler — `flutter build linux` toolchain front-end
#   cmake             build-system generator — required by `flutter build linux`
#   xvfb              X virtual framebuffer (no display server on host required)
#   libgtk-3-0        GTK 3 runtime — Flutter Linux desktop renders via GTK
#   libgtk-3-dev      GTK 3 build headers — required by `flutter build linux`
#   libblkid-dev      block-id headers — flutter_linux pulls these in
#   liblzma-dev       LZMA headers — flutter_linux pulls these in
#   ninja-build       Flutter Linux's build backend
#   pkg-config        used by ninja/cmake to locate GTK
#   libsecret-1-dev   common Flutter plugin dependency (secure storage etc.)
#   libnotify-dev     required by the `local_notifier` plugin (Linux desktop)
#   libayatana-appindicator3-dev  required by the `tray_manager` plugin (Linux desktop)
#   mesa-utils        software-rendered OpenGL for headless GL contexts
#   libegl1-mesa-dev  EGL headers — required by some Flutter renderers
#   libgl1-mesa-dri   DRI driver — software rasterization under Xvfb
PACKAGES=(
    clang
    cmake
    xvfb
    libgtk-3-0
    libgtk-3-dev
    libblkid-dev
    liblzma-dev
    ninja-build
    pkg-config
    libsecret-1-dev
    libnotify-dev
    libayatana-appindicator3-dev
    mesa-utils
    libegl1-mesa-dev
    libgl1-mesa-dri
)

echo "[install_linux_desktop_deps] Updating apt index…"
sudo apt-get update -qq

echo "[install_linux_desktop_deps] Installing: ${PACKAGES[*]}"
sudo apt-get install -y --no-install-recommends "${PACKAGES[@]}"

echo "[install_linux_desktop_deps] Done."
