{
  description = "A tool for automatically searching various academic libraries.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      rec {
        packages = rec {
          qal = pkgs.python3.pkgs.buildPythonPackage {
            pname = "qal";
            version = "1.0.0";
            src = ./.;
            propagatedBuildInputs = with pkgs.python3.pkgs ; [
              urllib3
              requests
              backoff
              jsonpickle
              tqdm
            ];
          };

          pythonEnvironment = pkgs.python3.withPackages (ps: with ps; [
            urllib3
            requests
            backoff
            jsonpickle
            tqdm
            qal
            build
            twine
            ipython
          ]);

          developmentEnvironment = pkgs.mkShell {
            buildInputs = [
              packages.pythonEnvironment
              pkgs.pre-commit
            ];
          };
        };
        defaultPackage = packages.qal;
        devShell = packages.developmentEnvironment;
      }
    );
}
