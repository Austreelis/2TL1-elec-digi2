{
  inputs = {
    nixpkgs.url = "nixpkgs";
    devshell = {
      url = "github:numtide/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    firmware = {
      url = "http://micropython.org/download/rp2-pico/rp2-pico-latest.uf2";
      flake = false;
    };
    rp2040js = {
      url = "github:wokwi/rp2040js";
      flake = false;
    };
  };

  outputs = inputs: let
    inherit (inputs) devshell nixpkgs self;
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

          {
            name = "rp2040";
            help = "micropython emulator in Typescript by wokwi";
            category = "micropython";
            command = ''
              echo "CTRL+X TO QUIT"
              npm run start:micropython --prefix ''${PRJ_DATA_DIR}/rp2040 -- \
                --image=${inputs.firmware} $@
            '';
          }
        ];

        devshell.packages = [
          pkgs.nodejs-16_x
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
            chmod +x "$PRJ_DATA_DIR"/venv/bin -R
          fi
          "$PRJ_DATA_DIR"/venv/bin/activate
        '';

        # Ensure node modules are installed
        devshell.startup.npm-install.text = ''
          mkdir -p "$PRJ_DATA_DIR"
          if ! [ -d "$PRJ_DATA_DIR"/rp2040 ]; then
            cp -rn ${inputs.rp2040js} ''${PRJ_DATA_DIR}/rp2040
            chmod +w ''${PRJ_DATA_DIR}/rp2040 -R
            sed -i 's/"prepare": "husky install",//' ''${PRJ_DATA_DIR}/rp2040/package.json
          fi
          if ! [ -d "$PRJ_DATA_DIR"/rp2040/node_modules ]; then
              npm --prefix ''${PRJ_DATA_DIR}/rp2040 install --no-audit --no-fund
          fi
        '';
      };
    in {
      devShells.${system} = mapAttrs (_: pkgs.devshell.mkShell) shells;
    };
  in foldl' recursiveUpdate { } (lists.map mkOutputs systems);
}
