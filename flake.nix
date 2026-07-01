{
  description = "FlowerMD :D";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
  };

  outputs = inputs@{ flake-parts, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } ({ ... }: {
    systems = import inputs.systems;

    perSystem = { pkgs, self', ... }: {
      devShells.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          conda
        ];
      };
    };
  });
}
