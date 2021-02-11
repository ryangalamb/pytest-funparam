{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python37
    python37Packages.virtualenv
    python38
    python39
  ];
  shellHook = ''
    VENV_DIR="$PWD"/env
    if [[ ! -e $VENV_DIR ]]; then
      virtualenv -p python3.7 env
    fi

    . "$VENV_DIR"/bin/activate

    # Get rid of PYTHONPATH. We don't need it, and tox makes a bunch of noise
    # about it.
    unset PYTHONPATH
  '';
}
