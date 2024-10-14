{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    fix-python.url = "github:GuillaumeDesforges/fix-python";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    fix-python,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {inherit system;};
        devEnv = pkgs.mkShell {
          buildInputs = with pkgs; [
            fix-python.packages.${system}.default
            python312
            ruff
            ruff-lsp
          ];

          shellHook = ''
            set -euo pipefail
            test -d .venv || (${pkgs.python312.interpreter} -m venv .venv && source .venv/bin/activate && pip install -e . && fix-python --venv .venv)
            source .venv/bin/activate
          '';
        };
        mypkg = pkgs.python312Packages.buildPythonPackage {
          pname = "quicktranslate";
          version = "0.0.2";
          src = ./.;
          format = "pyproject";
          nativeBuildInputs = [pkgs.python312Packages.setuptools];
          propagatedBuildInputs = with pkgs.python312Packages; [requests tkinter xdg-base-dirs pkgs.wl-clipboard-x11];
        };
      in {
        devShell = devEnv;
        packages.quicktranslate = mypkg;
        defaultPackage = mypkg;
      }
    );
}
