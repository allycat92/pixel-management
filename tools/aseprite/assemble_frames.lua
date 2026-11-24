local src = app.params["src"]; local out = app.params["out"]
local spr = Sprite(48, 56, ColorMode.RGB)
local layer = spr.layers[1]; layer.name = "baren"
local durs = {0.24,0.24,0.24,0.24, 0.12,0.12,0.12,0.12, 0.08,0.08,0.06,0.10,0.14, 0.20}
for i = 1, 14 do
  if i > 1 then spr:newEmptyFrame(i) end
  local img = Image{ fromFile = string.format("%s/f%02d.png", src, i-1) }
  spr:newCel(layer, i, img, Point(0,0))
  spr.frames[i].duration = durs[i]
end
local function tag(a,b,name,col) local t = spr:newTag(a,b); t.name = name; t.color = col end
tag(1,4,"idle",Color{r=90,g=160,b=90}); tag(5,8,"walk",Color{r=90,g=120,b=200})
tag(9,13,"attack",Color{r=200,g=80,b=70}); tag(14,14,"hit",Color{r=220,g=200,b=80})
spr:saveAs(out .. "/baren.aseprite")
