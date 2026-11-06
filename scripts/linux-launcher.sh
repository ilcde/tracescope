#!/bin/sh
set -eu
app_dir=$(CDPATH= cd -- "$(dirname -- "$(readlink -f -- "$0")")" && pwd)
python_tag=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
expected=$(cat "$app_dir/python-version")
if [ "$python_tag" != "$expected" ]; then
  echo "This package needs Python $expected; found $python_tag. Install the package for your distribution." >&2
  exit 1
fi
state_dir=${TRACESCOPE_DATA_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/tracescope}
runtime_dir="$state_dir/runtime-$python_tag"
mkdir -p "$state_dir"
wheel_hash=$(cat "$app_dir/wheels.sha256")
if [ ! -x "$runtime_dir/bin/python" ] || [ ! -f "$runtime_dir/.installed" ] || [ "$(cat "$runtime_dir/.installed")" != "$wheel_hash" ]; then
  python3 -m venv --system-site-packages "$runtime_dir"
  "$runtime_dir/bin/python" -m pip install --no-index --find-links "$app_dir/wheels" -r "$app_dir/requirements.txt"
  printf '%s' "$wheel_hash" > "$runtime_dir/.installed"
fi
export TRACESCOPE_DATA_DIR="$state_dir"
export PYTHONPATH="$app_dir${PYTHONPATH:+:$PYTHONPATH}"
export PYWEBVIEW_GUI=${PYWEBVIEW_GUI:-gtk}
if [ "$#" -eq 0 ]; then set -- desktop; fi
exec "$runtime_dir/bin/python" -m tracescope "$@"
