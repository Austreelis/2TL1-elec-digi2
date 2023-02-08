{
  inputs = {
    nixpkgs.url = "nixpkgs";
    devshell.url = "github:numtide/devshell";
  };

  outputs = inputs: let
    inherit (inputs) devshell nixpkgs;
    inherit (nixpkgs.lib) foldl' lists mapAttrs recursiveUpdate;

    # Supported host systems
    systems = [
      "x86_64-linux"
    ];

    mkOutputs = system: let
      # Package set
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ devshell.overlays.default or devshell.overlay ];
      };

      # Default development shell
      shells.default = {
        devshell.name = "2tl1-elec-digi2";

        commands = [
          {
            name = "python";
            category = "python";
            command = "python3";
            package = pkgs.python310;
          }
          { package = pkgs.python310Packages.black; category = "python"; }
          
          { package = pkgs.micropython; category = "micropython"; }
          { package = pkgs.rshell; category = "micropython"; }
        ];

        devshell.packages = [
          pkgs.python310Packages.python-lsp-black
          pkgs.python310Packages.python-lsp-server
        ];

        env = [
          # Add venv executables to $PATH
          {
            name = "PATH";
            eval = ''"''${PATH:+$PATH:}''${PRJ_DATA_DIR}/venv/bin"'';
          }
        ];
        
        # Enter python venv at shell startup
        devshell.startup.py-venv.text = ''
          mkdir -p "$PRJ_DATA_DIR"
          if ! [ -x "$PRJ_DATA_DIR"/venv/bin/activate ]; then
            python -m venv "$PRJ_DATA_DIR"/venv
          fi
          "$PRJ_DATA_DIR"/venv/bin/activate
        '';
      };
    in {
      devShells.${system} = mapAttrs (_: pkgs.devshell.mkShell) shells;
    };
  in foldl' recursiveUpdate { } (lists.map mkOutputs systems);
}
