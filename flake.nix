{
  description = "A flake for the quicktranslate project";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      mypkg = pkgs.python3Packages.buildPythonPackage {
        pname = "quicktranslate";
        version = "0.0.1";
        src = self;
        format = "pyproject";
        nativeBuildInputs = [pkgs.python3Packages.setuptools];
        propagatedBuildInputs = with pkgs.python3Packages; [requests tkinter xdg-base-dirs pkgs.wl-clipboard-x11];
      };
    in {
      packages.quicktranslate = mypkg;
      defaultPackage = mypkg;
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          (python3.withPackages (ps: [
            mypkg
          ]))
        ];
      };
    });
}
