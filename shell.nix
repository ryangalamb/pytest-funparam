with import <nixpkgs> {};
let
  pyPackages = ps: [
    ps.setuptools
    ps.tox
  ];
in mkShell {
  buildInputs = [
    # NOTE: need to use `withPackages` for all python derivations, otherwise
    #       environment variables will leak.
    (python36.withPackages pyPackages)
    (python37.withPackages pyPackages)
    (python38.withPackages pyPackages)
    (python39.withPackages pyPackages)
  ];
  shellHook = ''
    # Set up the development virtualenv.
    tox -e dev
    # Activate the development virtualenv.
    . env/bin/activate
  '';
}
