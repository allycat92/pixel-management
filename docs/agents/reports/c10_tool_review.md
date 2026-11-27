C10 TOOL REVIEW (adversarial). I changed nothing in the repo; all tests ran in scratch or with --dry-run. The one modified file in the working tree, docs/plans/battle_stats/stage3_notes.md, is not mine; the Stage 4 workflow running alongside is changing it. manifest.json and sheet_captain_frostjarl.png md5 were the same before and after the add_gait runs.

FINDINGS, most severe first

1. [HIGH, new in C10] run_request_guides.build() now silently rescales the mannequin for any scale mismatch, including when the scale itself was derived wrongly. Before C10 the tool raised Fail on a mismatch. Now a bad scale turns into a broken request that --check accepts, because --check uses the same derivation.
   - Frost troll: `python3 tools/art/run_request_guides.py "sheet/monster/서리 트롤" --info` gives scale 0.0812, "from registered idle height". Its source is a 2x2 grid, but geometry() treats it as a 1x4 strip: idle_x 159-567, idle_top 50, idle_low 973.
   - Building it into scratch (--out) gives scale_ratio 2.037, step_px 290.26, head_px 224. Frame top_px is -6/8/-2/-4 (above the canvas). In the size image the mannequin is about 2x the troll and clipped at the slot edges (seen by eye).
   - Codex's report table says the troll is 0.18 "from the registration record", but the tool has no such source. `gait_requests.py --write` would produce this request.
   - Goblin: geometry gives 0.1687 (no phase3 scale), so the tool writes a ×0.980 scaled request (step_px 269.62). Codex's table says the goblin was registered at 0.1654, which needs no scaling.
   - Neither is in phase3.json, so add_gait needs --scale, and the generated SELF-CHECK command has no --scale, so it fails for Antigravity.
   - Fix: only scale when the scale comes from phase3.json (scale_src). Otherwise Fail. Also Fail if the scaled mannequin's top < 0 or any pixel falls outside x 32..351. With ratio > 1 nothing guards the slot band; run_base already reaches x=351.

2. [MEDIUM, new] The scaled request still offers the unscaled mannequin as a drawing underlay.
   - run__captain_frostjarl/README.md says "art/requests/guides/run_base/v2/run_base.aseprite (the mannequin source - you may open it as an underlay and draw on your own layers ...)". The file table also lists guides/run_base/v2/ as the mannequin source.
   - That .aseprite is at 0.1654, about 8.8% larger than the scaled guide. Antigravity works in Aseprite, so a trace over it would be drawn too big. Its planted-toe x would also be the unscaled ones (290/222/155) instead of the README's 282/220/158.
   - check_delivery cannot catch this. add_gait would convert at 0.18, so in-game run frames would be about 9% larger than the idle.
   - Fix: for scaled requests, either write a scaled .aseprite underlay or tell the artist to use only guide_run_a/b.png and not the .aseprite.

3. [MEDIUM, new gap] `gait_requests.py` status (default view and --json) still gives the class mannequin as --pose in the frostjarl "attach" command.
   - The --json row reads `--pose art/requests/guides/run_base/v2/pose.json`.
   - Running that command as a dry-run on the warrior-drawing copy gives runStride 49.5, not 45.5.
   - status() uses guide_of(cls) and never checks for the request-local pose.json.
   - The index row in art/requests/gait/README.md also lists the mannequin as `run_base/v2` (that one is only informational).

4. [MEDIUM, pre-existing but hits C10's next targets] receive.py works out the sheet id from the png stem (`'sheet/' + body.replace('_','/',1)`).
   - The goblin and frost troll ids in the manifest are Korean (`sheet/monster/고블린`, `sheet/monster/서리 트롤`).
   - So gait_class('sheet_monster_frost-troll') returns None, the sheet is treated as light, and receive looks for run__monster_frost-troll/pose.json.
   - A heavy, scaled troll request lives in heavy__monster_frost-troll, so receive would not find it. It would use run_base (stride 275) with --flight-slots 4, and a correct heavy delivery would fail the flight check.
   - run_request_guides and gait_requests already map stem to id through the manifest; receive should do the same.

5. [LOW] The README check in --check only needs one `--pose <expected>` match.
   - In a scratch copy I changed the last `--pose` (in SELF-CHECK) back to the class mannequin and left the line-22 one correct; --check still passed.
   - README numbers (step, planted toe x) are never compared with the pose either. Regenerating the README and diffing it, minus the date, would close both gaps.

6. [LOW] For heavy/robe, scale_pose leaves `check` thresholds unscaled (hem_min_px 38, hand_height_px [165,230], lifted_sole_px ...). It also leaves `measured_frames` joints at source scale while `frames` are scaled.
   - That makes the local pose.json internally inconsistent. Nothing reads these for requests today; check_skeleton.py would if pointed at it.
   - The README's "lifted sole 3-13 px" also uses the unscaled default of 13.

7. [LOW, nits]
   - The pose top_px rounding differs from the image by 1 px: R3/R7 pose says 490, the scaled guide's top is 491.
   - The README prints "head 101.078 px".
   - With --out, pose paths in the README become `../../tmp/...` (test only). On Windows, relpath across drives raises ValueError, and only in scaled mode.
   - build() writes pose.json before the images, so a font failure leaves an orphan pose.json.
   - add_gait.draft_masks and receive.gait_pose json.load every request pose.json with no try. One malformed pose.json in any request folder crashes add_gait for every sheet with a traceback.
   - Nearest-neighbour downscale thins the outline in places: 1-px dark horizontal runs went from 7 to 49. It looks fine by eye.

8. [INFO, pre-existing] The committed size_* text is not reproducible from the committed tool.
   - FONT is hard-coded to the DejaVu path. Codex generated on Windows with Arial, which is not in the tree.
   - Committed frostjarl and bard size_* differ from a Linux regen only in the text bands; outside y 365-880 the pixel diff is 0.
   - Committed C8 READMEs (bard and others) carry hand-edited CARRY/CHARACTER text that the tool no longer produces, so `--write --force` would overwrite those edits.

WHAT PASSED
- (1) Unscaled requests are unchanged. I ran the pre-C10 tool (c57bd07^, git archive in scratch) and the new tool on the same inputs:
  - guide_* and size_* are byte-identical for run__captain_bard, heavy__captain_ironwall, robe__class_mage and run__class_archer.
  - `gait_requests.py --write --out` README text is identical for bard, ironwall, mage, hero_grom and hero_astel.
- Frostjarl regenerated into scratch: guide_run_a/b are pixel-identical to the committed ones and pose.json is byte-identical. size_* differ only in text (font).
- Scaled guides keep the soles on y=870 (lowest row 870; flight frames 849/848, so flight clearance is still at least 18) and the hip column 192.
- (2) add_gait --dry-run with `--pose art/requests/gait/run__captain_frostjarl/pose.json`:
  - The warrior-drawing copy passes with runStride 45.5, the same as warrior on its own sheet with the standard pose (45.5).
  - Floor y=870 maps to cell y=92.04 (anchor 92) and x=192 to 48.00 (anchor 48).
  - The scaled-guide copy is REFUSED: IoU 1.000 against the request guide.
  - Even with the new request-local guides removed from draft_masks, the existing height match catches it: ratio 0.919 gives 0.992. Copies scaled ×0.95, ×0.85 and ×1.1 give 0.997, 0.991 and 0.995.
- (3) receive.gait_pose('sheet_captain_frostjarl','run') returns art/requests/gait/run__captain_frostjarl/pose.json (step_px 252.6944, scale 0.18). Bard, ironwall and mage still get their class mannequins; frostjarl walk still gets walk_base/v2.
- (4) --check on a scratch copy of HEAD: baseline PASS (27 requests). It FAILs correctly when:
  - pose.json is missing;
  - pose.json has a stale step_px;
  - pose.json is an unscaled copy of the class pose;
  - a stray pose.json sits in a standard request;
  - the guide has a 1-px edit;
  - the mannequin source changes;
  - the README points only at the class pose.
  A re-serialised but equal pose.json passes. The one gap is finding 5.
- Live repo `gait_requests.py --check`: RESULT PASS (54 sheets, 27 requests).
- Path separators: scaled_from, pj and rel() normalise to `/`; add_gait.rel() normalises the stored rec.pose.

Scratch outputs are in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/ (regen/, troll/, gob/, t2/, cur/, old/). The broken troll guide is /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/troll/size_heavy_a.png.