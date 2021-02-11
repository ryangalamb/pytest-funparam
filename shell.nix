with import <nixpkgs> {};
let
  basePythonEnv = python37.withPackages (ps: [
    ps.setuptools
    ps.tox
  ]);
in mkShell {
  buildInputs = [
    basePythonEnv
    python38
    python39
  ];
  shellHook = ''
    # Get rid of PYTHONPATH. We don't need it, and tox makes a bunch of noise
    # about it.
    unset PYTHONPATH
    # Set up the development virtualenv.
    tox -e dev
    # Activate the development virtualenv.
    . env/bin/activate
  '';
}
