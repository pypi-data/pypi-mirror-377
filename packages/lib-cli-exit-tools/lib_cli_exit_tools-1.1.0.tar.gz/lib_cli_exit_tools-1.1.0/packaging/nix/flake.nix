{
  description = "lib_cli_exit_tools Nix flake";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        lib = pkgs.lib;
        pypkgs = pkgs.python310Packages;

        # Vendor hatchling>=1.25 from PyPI (wheel) to satisfy PEP 517 build
        hatchlingVendor = pypkgs.buildPythonPackage rec {
          pname = "hatchling";
          version = "1.25.0";
          format = "wheel"; # install straight from wheel to avoid circular build-backend
          # Use explicit URL for py3 wheel; nixpkgs 24.05 fetchPypi may choose a py2.py3 path.
          src = pkgs.fetchurl {
            url = "https://files.pythonhosted.org/packages/py3/h/hatchling/${pname}-${version}-py3-none-any.whl";
            hash = "sha256-tHlI5F1NlzA0WE3UyznBS2pwInzyh6t+wK15g0CKiCw=";
          };
          propagatedBuildInputs = [
            pypkgs.packaging
            pypkgs.tomli
            pypkgs.pathspec
            pypkgs.pluggy
            pypkgs."trove-classifiers"
            pypkgs.editables
          ];
          doCheck = false;
        };
      in
      {
        packages.default = pypkgs.buildPythonPackage {
          pname = "lib_cli_exit_tools";
          version = "1.1.0";
          pyproject = true;
          # Build from the repository root (two levels up from packaging/nix)
          src = ../..;
          # For pinned releases, swap src for fetchFromGitHub with a rev/sha256.
          # src = pkgs.fetchFromGitHub {
          #   owner = "bitranox";
          #   repo = "lib_cli_exit_tools";
          #   rev = "v1.1.0";
          #   sha256 = "<fill-me>";
          # };

          # Ensure PEP 517 backend is available at required version
          # Ensure PEP 517 backend available at required version (>=1.25)
          nativeBuildInputs = [ hatchlingVendor ];
          propagatedBuildInputs = [ pypkgs.click ];

          meta = with pkgs.lib; {
            description = "CLI exit handling helpers: clean signals, exit codes, and error printing";
            homepage = "https://github.com/bitranox/lib_cli_exit_tools";
            license = licenses.mit;
            maintainers = [];
            platforms = platforms.unix ++ platforms.darwin;
          };
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python310
            hatchlingVendor
            pypkgs.click
            pypkgs.pytest
            pkgs.ruff
            pkgs.nodejs
          ];
        };
      }
    );
}
