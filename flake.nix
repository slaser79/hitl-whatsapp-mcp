{
  description = "HITL WhatsApp MCP — Go whatsmeow bridge + Python FastMCP server";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Keep these in sync with whatsapp-bridge/go.mod and
        # whatsapp-mcp-server/pyproject.toml.
        # nixpkgs-unstable's default `go` (1.26.x) builds the go.mod's
        # `go 1.24.1` requirement fine. Pin explicitly if drift becomes an issue.
        goVersion = pkgs.go;
        pythonVersion = pkgs.python312;

        # Reproducible build of the Go whatsmeow bridge.
        #
        # The Go module is named `whatsapp-client` (see whatsapp-bridge/go.mod),
        # so the produced binary is `bin/whatsapp-client`. go-sqlite3 needs CGO,
        # hence CGO_ENABLED=1 and a C toolchain in nativeBuildInputs.
        #
        # vendorHash must be refreshed whenever go.mod / go.sum change:
        #   nix build .#whatsapp-bridge   # copy the "got:" hash from the error
        whatsapp-bridge = pkgs.buildGoModule {
          pname = "whatsapp-bridge";
          version = "0.2.1";
          src = ./whatsapp-bridge;
          vendorHash = "sha256-+wkxy825hAFrCHPMhJoWt3EMtRCKxB+g7jCfj7R9g4k=";

          go = goVersion;

          env.CGO_ENABLED = "1";
          nativeBuildInputs = [ pkgs.pkg-config ];
          # mattn/go-sqlite3 vendors its own SQLite amalgamation and compiles it
          # via CGO, so the build needs only a C toolchain (already provided by
          # buildGoModule). SQLite is listed explicitly to make the C dependency
          # intent clear and future-proof against build-tag changes.
          buildInputs = [ pkgs.sqlite ];

          # The whatsmeow bridge has no Go test files wired for `go test`; skip
          # the check phase to keep the build hermetic and fast.
          doCheck = false;

          meta = with pkgs.lib; {
            description = "WhatsApp Web bridge (whatsmeow) for the HITL WhatsApp MCP server";
            homepage = "https://github.com/slaser79/hitl-whatsapp-mcp";
            license = licenses.mit;
            mainProgram = "whatsapp-client";
            platforms = platforms.unix;
          };
        };
      in
      {
        packages = {
          inherit whatsapp-bridge;
          default = whatsapp-bridge;
        };

        apps.whatsapp-bridge = {
          type = "app";
          program = "${whatsapp-bridge}/bin/whatsapp-client";
        };
        apps.default = self.apps.${system}.whatsapp-bridge;

        devShells.default = pkgs.mkShell {
          name = "hitl-whatsapp-mcp";

          packages = [
            # Go bridge toolchain (CGO for go-sqlite3 → needs a C compiler)
            goVersion
            pkgs.gcc
            pkgs.pkg-config
            pkgs.golangci-lint

            # Python MCP server toolchain
            pythonVersion
            pkgs.uv

            # Runtime / ops helpers
            pkgs.ffmpeg # voice-message conversion to Opus .ogg
            pkgs.openssl # token generation (openssl rand -hex 24)
            pkgs.tailscale # remote serve flow (scripts/run-tailscale-serve.sh)
            pkgs.sqlite # inspect messages.db / whatsapp.db
          ];

          # Let uv use the Nix-provided interpreter instead of downloading one.
          env.UV_PYTHON_DOWNLOADS = "never";

          # Banner goes to stderr so `nix develop -c <cmd>` command substitutions
          # (e.g. $(nix develop -c openssl rand -hex 24)) capture only <cmd>'s
          # stdout, not this shell-hook text.
          shellHook = ''
            {
              echo "hitl-whatsapp-mcp dev shell"
              echo "  go      : $(go version 2>/dev/null)"
              echo "  python  : $(python3 --version 2>/dev/null)"
              echo "  uv      : $(uv --version 2>/dev/null)"
              echo "  ffmpeg  : $(ffmpeg -version 2>/dev/null | head -n1)"
              echo
              echo "Bridge : cd whatsapp-bridge && go run ."
              echo "Server : cd whatsapp-mcp-server && uv run main.py"
              echo "Or build the bridge via nix: nix build .#whatsapp-bridge"
            } >&2
          '';
        };
      }
    );
}
