#!/usr/bin/env bash

set -euo pipefail

function usage () {
  echo "Flash MicroPython on tinyfs-enabled boards:"
  echo "  flash_micropy.sh -m [-fs] [-d device] [path]"
  echo
  echo "Flash a MicroPython script using rshell:"
  echo "  flash_micropy.sh -s [-d device]"
  echo
  echo "Display this help:"
  echo "  flash_micropy.sh -h|--help"
  echo
  echo "OPERATIONS"
  echo
  echo " -m --micropython        Flash MicroPython on a tinyfs"
  echo " -s --script             Flash a micropython script via rshell"
  echo
  echo "FLASH MICROPYTHON OPTIONS"
  echo "  -m --micropy           Flash MicroPython."
  echo "  -f --force             Force renaming the board's main.py."
  echo "                         Useful to repair bricked devices."
  echo "  -s --script            Also flash script after flashing micropython."
  echo
  echo "FLASH SCRIPT OPTIONS"
  echo "  -t --timeout <seconds> Maximum time to wait for a serial port."
  echo
  echo "COMMON OPTIONS"
  echo "  -h --help              Print this help and exit."
  echo "  -d --device <device>   Block device to flash. Ignored when flashing"
  echo "                         MicroPython at the same time"
}

do_flash_mpy=
do_force=
do_flash_script=
mount_path=
device_path=

while [ -v 1 ]; do
  opt="$1"
  case $opt in
    -f|--force)
      do_force=yes
      ;;
    -s|--flash-script)
      do_flash_script=yes
      ;;
    -m|--micropython)
      do_flash_mpy=yes
      ;;
    -t|--timeout)
      if [ -z "${2:-}" ]; then
        usage >&2
        echo "$1 specified but no <seconds> given" >&2
        exit 1
      fi
      shift
      timeout="-w $1"
      ;;
    -d|--device)
      if [ -z "${2:-}" ]; then
        usage >&2
        echo "$1 specified but no <device> given" >&2
        exit 1
      elif [ -n "$mount_path" ]; then
        usage >&2
        echo "$1 given but a mount was already specified" >&2
        exit 1
      fi
      shift
      device_path="$1"
      ;;
    *)
      if [ -n "${2:-}" ] || [ -z "$do_flash_mpy" ]; then
        usage >&2
        echo "Unknown argument: $1" >&2
        exit 1
      fi
      mount_path="$1"
  esac
  shift
done

if [ -n "$do_flash_mpy" ]; then
  tmp_mount=

  if [ -n "$device_path" ]; then
    tmp_mount=$(mktemp -d -p . -t flash-micropy-tmpmount.XXX)
    mount "$device_path" "$tmp_mount"
    mount_path="$tmp_mount"
  elif [ -z "$mount_path" ]; then
    usage >&2
    echo "Need one of -m or -d, but none were specified" >&2
    exit 1
  fi

  if [ -n "$do_force" ]; then
    cp \
      "${MPY_RENAME_MAIN_UF2:-${PRJ_ROOT:-./}utils/Micropython_RenameMain.uf2}" \
      "$mount_path/micropython_rename_main.uf2"

    read -N 1 -p "Press any key when the device is done rebooting..."

    if [ -z "$device_path" ]; then
      read -N 1 -p "Redo the flashing procedure and remount the board's tinyfs,\nthen press any key..."
    else
      read -N 1 -p "Redo the flashing procedure, then press any key..."
      mount "$device_path" "$tmp_mount"
    fi
  fi

  curl "https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2" \
    > "$mount_path/micropython_latest.uf2"

  if [ -n "$do_flash_script" ] || [ -n "$tmp_mount" ]; then
    read -N 1 -p "Press any key when the device is done rebooting..."
  fi

  if [ -n "$tmp_mount" ]; then
    rm -rf "$tmp_mount" \
    || echo "Cannot remove temp mount directory $tmp_mount: you'll have to do it yourself" >&2
  fi
fi

if [ -n "$do_flash_script" ]; then
  rshell ${timeout:-} \
    -f "${RSHELL_FLASH_SCRIPT:-${PRJ_ROOT:-.}/flash_script.rsh}" \
    2>/dev/null
fi

