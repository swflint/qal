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
          scrape-acad-library = pkgs.python3.pkgs.buildPythonPackage {
            pname = "scrape_acad_library";
            version = "0.5.0";
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
            scrape-acad-library
            ipython
          ]);

          developmentEnvironment = pkgs.mkShell {
            buildInputs = [
              packages.pythonEnvironment
              pkgs.pre-commit
            ];
          };
        };
        defaultPackage = packages.scrape-acad-library;
        devShell = packages.developmentEnvironment;
      }
    );
}
