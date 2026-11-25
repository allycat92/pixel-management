-- Builds a layered, animated .aseprite from per-frame layer PNGs (written by tools/pixelart/walk8.py).
--   aseprite -b --script-param dir=<layers dir> --script-param out=<file.aseprite> --script-param frames=8 \
--            --script-param ms=120 --script tools/pixelart/build_skeleton_ase.lua
-- Layers bottom to top: Background (#FF00FF) / arm_far / leg_far / leg_near / torso / head / arm_near / joints (hidden).
local p = app.params
local dir, out = p.dir, p.out
local n = tonumber(p.frames) or 8
local ms = tonumber(p.ms) or 120
local names = { "arm_far", "leg_far", "leg_near", "torso", "head", "arm_near", "joints" }
local first = Image{ fromFile = dir .. "/W1_torso.png" }
local spr = Sprite(first.width, first.height, ColorMode.RGB)
local bg = spr.layers[1]
bg.name = "Background"
for f = 2, n do spr:newEmptyFrame(f) end
for f = 1, n do
  local img = Image(spr.width, spr.height, ColorMode.RGB)
  img:clear(Color{ r = 255, g = 0, b = 255, a = 255 })
  spr:newCel(bg, f, img, Point(0, 0))
  spr.frames[f].duration = ms / 1000.0
end
for _, name in ipairs(names) do
  local l = spr:newLayer()
  l.name = name
  for f = 1, n do
    local im = Image{ fromFile = dir .. "/W" .. f .. "_" .. name .. ".png" }
    spr:newCel(l, f, im, Point(0, 0))
  end
  if name == "joints" then l.isVisible = false end
end
spr:saveAs(out)
