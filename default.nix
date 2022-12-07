let
  nixpkgs = builtins.fetchGit {
    url = "https://github.com/nixos/nixpkgs/";
    ref = "refs/heads/nixos-unstable";
    rev = "f2537a505d45c31fe5d9c27ea9829b6f4c4e6ac5"; # 27-06-2022
    # obtain via `git ls-remote https://github.com/nixos/nixpkgs nixos-unstable`
  };
  pkgs = import nixpkgs { config = {}; };
  ropemode = with pkgs.python39Packages; buildPythonPackage rec {
    pname = "ropemode";
    version = "0.6.1";

    src = fetchPypi{
      inherit version;
      inherit pname;
      sha256 = "sha256:0w04vm25f729f95bsimq886aamqf2jbzndf41khmiqqvywnx5f4r";
    };

    # TODO: See if I can enable this
    doCheck = false;

    buildInputs = [ rope ];
  };
  ropevim = with pkgs.python39Packages; buildPythonPackage rec {
    pname = "ropevim";
    version = "0.8.1";

    src = fetchPypi{
      inherit version;
      inherit pname;
      sha256 = "sha256:099pcbyxmyxi60bp4r8vkk04vvr37vy5nzpvgir62kz5kgsdr5bp";
    };

    # TODO: See if I can enable this
    doCheck = false;

    buildInputs = [ rope ropemode ];
  };
  
  pythonPkgs = python-packages: with python-packages; [
    pydantic

    # TODO: propagate build inputs I guess
    #ropemode
    #rope

    # dev
    pytest
    ptpython
    #ropevim
    #pynvim
  ];
  pythonCore = pkgs.python39;
  myPython = pythonCore.withPackages pythonPkgs;
in
pkgs.mkShell {
  buildInputs =
  with pkgs;
  [
    git
    gnumake
    myPython
    python-language-server
  ];
}
