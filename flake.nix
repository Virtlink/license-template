{
  description = "Development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: import nixpkgs {
        system = if system == "x86_64-darwin" then "aarch64-darwin" else system;
      };
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = pkgsFor system;
          python = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.copier
            ];
          };
        });

      apps = forAllSystems (system:
        let
          pkgs = pkgsFor system;
          python = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
          updateLicenses = pkgs.writeShellApplication {
            name = "update-licenses";
            runtimeInputs = [ python ];
            text = ''
              exec ${python}/bin/python ${./update-licenses.py}
            '';
          };
        in
        {
          default = {
            type = "app";
            program = "${updateLicenses}/bin/update-licenses";
          };
        });
    };
}
