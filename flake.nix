{
  description = "Development environment for tlserver";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.tabler-icons = {
    url = "github:tabler/tabler-icons";
    flake = false;
  };

  outputs =
    { nixpkgs, tabler-icons, ... }:
    let
      supportedSystems = [
        "aarch64-linux"
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          tablerIconFont = pkgs.stdenv.mkDerivation {
            pname = "tabler-icons-font";
            version = "unstable";
            src = tabler-icons;

            pnpmDeps = pkgs.fetchPnpmDeps {
              pname = "tabler-icons-font";
              version = "unstable";
              src = tabler-icons;
              pnpm = pkgs.pnpm_10;
              pnpmWorkspaces = [ "@tabler/icons-webfont" ];
              fetcherVersion = 3;
              hash = "sha256-jZsdVsefxfwdGGa1MhtQ42qPCRz512EpR56aFEMBLhY=";
            };

            nativeBuildInputs = [
              pkgs.nodejs
              pkgs.pnpm_10
              pkgs.pnpmConfigHook
              pkgs.pkg-config
              pkgs.python3
            ];

            buildInputs = [
              pkgs.cairo
              pkgs.pango
              pkgs.libjpeg
              pkgs.giflib
              pkgs.librsvg
            ];

            pnpmWorkspaces = [ "@tabler/icons-webfont" ];
            npm_config_build_from_source = true;
            buildPhase = ''
              pnpm rebuild canvas
              pnpm --filter @tabler/icons-webfont build
            '';

            installPhase = ''
              install -Dm644 packages/icons-webfont/dist/fonts/tabler-icons.ttf \
                "$out/share/fonts/truetype/tabler-icons.ttf"
              install -Dm644 packages/icons-webfont/dist/fonts/tabler-icons-filled.ttf \
                "$out/share/fonts/truetype/tabler-icons-filled.ttf"
            '';
          };
          fonts = [
            pkgs.atkinson-hyperlegible-next
            pkgs.fantasque-sans-mono
            pkgs.noto-fonts-cjk-sans
            pkgs.noto-fonts-cjk-serif
            (pkgs.google-fonts.override {
              fonts = [
                "Arvo"
                "Figtree"
                "Fredoka"
                "Lato"
                "Nunito Sans"
                "Rubik"
                "Vollkorn"
              ];
            })
            tablerIconFont
          ];
        in
        {
          default = pkgs.mkShell {
            packages =
              with pkgs;
              [
                # Python dependencies remain managed by pyproject.toml and uv.lock.
                python311
                uv

                # Project development tools.
                basedpyright
                ruff
                cmake
                pkg-config
                stdenv.cc

                # Typst compiler, language server/preview support, and formatter.
                typst
                tinymist
                typstyle

                fontconfig
              ]
              ++ fonts;

            # Force uv to use the interpreter supplied by this shell.
            UV_PYTHON = "${pkgs.python311}/bin/python";
            UV_PYTHON_DOWNLOADS = "never";

            # Make Nix-provided fonts visible both to Typst and fontconfig.
            TYPST_FONT_PATH = pkgs.lib.makeSearchPath "share/fonts" fonts;
            FONTCONFIG_FILE = pkgs.makeFontsConf { fontDirectories = fonts; };

            # Native Python wheels such as ctranslate2 need the C++ runtime.
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
            ];
          };
        }
      );
    };
}
