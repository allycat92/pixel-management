# Aseprite (local build, Linux) — notes only

Aseprite's EULA allows building it for personal use but **forbids redistributing binaries**.
Never commit or publish the built `aseprite` binary. These notes follow
github.com/a1393323447/aseprite-builder (Linux job).

## Build (Ubuntu, ~40 min on 4 cores)

```bash
apt-get install -y g++ cmake ninja-build libx11-dev libxcursor-dev libxi-dev libxrandr-dev \
  libgl1-mesa-dev libfontconfig1-dev libssl-dev
git clone --recursive --branch v1.3.18.6 https://github.com/aseprite/aseprite.git src
# Skia m124 prebuilt: github.com/aseprite/skia/releases (Skia-Linux-Release-x64.zip) -> skia-pkg/
cmake -S src -B src/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DENABLE_TESTS=OFF \
  -DENABLE_SCRIPTING=on -DENABLE_CCACHE=off -DLAF_BACKEND=skia \
  -DSKIA_DIR=$PWD/skia-pkg -DSKIA_LIBRARY_DIR=$PWD/skia-pkg/out/Release-x64 -DOPENSSL_USE_STATIC_LIBS=ON
ninja -C src/build -j4
```

Run headless with a throwaway profile:
`HOME=$T XDG_CONFIG_HOME=$T/c ASEPRITE_USER_FOLDER=$T/a src/build/bin/aseprite -b ...`

## Assemble frames into a tagged .aseprite

`assemble_frames.lua` reads `f00.png..f13.png` (48x56) from `src` and writes `baren.aseprite`
with tags idle(1-4) / walk(5-8) / attack(9-13) / hit(14). Edit `durs` and the tag ranges for other characters.

```bash
aseprite -b --script-param src=FRAMES --script-param out=OUT --script tools/aseprite/assemble_frames.lua
aseprite -b OUT/baren.aseprite --sheet OUT/sheet.png --data OUT/sheet.json \
  --format json-array --list-tags --sheet-type rows --split-tags
```
