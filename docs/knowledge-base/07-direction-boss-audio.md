# Knowledge Base I — Direction, bosses, and sound

Entries T-73 … T-81. S14–S16 plus two engineering entries for a decision the build
transcripts never made: whether the game should exist.

---

## T-73 — Pick headless, MCP, or computer use

**Problem.** "Use MCP" and "never use MCP" are both wrong. The slow part of headless is
the full render used as a check, not the lack of a window.

**Why it works.** A timed test with one model and fresh sessions (S15): MCP won single-prop
speed; headless won cloth and an edit the tester expected MCP to win; computer-use was
slower, cost more, and produced a worse crate. Parallel headless gives each agent a
process and leaves a script.

**When.** Any Blender task that could go through a GUI, a live add-on, or a script.

**Inputs.** A Blender executable. MCP only if a live session is already wanted.

**Steps.**
1. Pipeline, many assets, or CI → headless (T-09).
2. One prop, someone is watching → MCP. Send the whole job as one call if other agents
   share that Blender.
3. Do not click the UI to model. Re-time this if the tool changes; the minutes in
   `skills/gamedev-blender-headless/references/mcp-vs-headless.md` are that test only.

**Fails when.** Five MCP agents share one scene and then cannot see their own prop.
Separate files, or use headless.

**Validate.** The chosen path either leaves a re-runnable script (headless) or a viewport
check the operator actually used (MCP). A stacked pile of five props is a failed MCP run.

**Recover.** If an edit looks smooth but the reference shows damage or cloth, switch to
headless for that asset. Seeing the object did not win the edit round.

**Skill.** `gamedev-blender-headless`.
**Basis.** transcript.
**Src.** S15 L43-50, L65-139, L141-229.

---

## T-74 — Play two greyboxes, keep one

**Problem.** Art production starts on a world nobody has played. The source built three
and kept one.

**Why it works.** Version one (floating city, wrap at the edge) had a lighting problem and
a layout the author did not love. Version two (city on the inside of a sphere) was fun
but lost the wrap. The kept game was the flat city plus the wrap, chosen after play, not
after a drawing (S14).

**When.** A new game, or a level idea, before kits and hero assets.

**Inputs.** Two playable greyboxes. Not two mood paintings.

**Steps.**
1. Build the smallest playable of each idea.
2. Play both. Write the one trick each has that you would miss.
3. Keep one world. You may steal the trick from the other. Bin the rest.
4. Only then measure art against target renders (existing visual-iteration loop).

**Fails when.** You "merge" by keeping every system from both. That is a third, larger game.

**Validate.** A sentence: which build was deleted, and which single trick survived.

**Recover.** If you cannot say what you deleted, you have not chosen. Stop art.

**Skill.** `gamedev-orchestrator`.
**Basis.** transcript.
**Src.** S14 L29-59.

---

## T-75 — Autopilot the scenario the designer won

**Problem.** A human win does not mean the objective works. Bombers in the source never
hit the reactor; towers around the square absorbed the shots. The designer still won.

**Why it works.** Three scripted runs, same scenario, showed a reactor stuck at full.
After the bombers were sent into the square, the same three runs damaged it (S14).

**When.** A loop can be finished by the person who built it.

**Inputs.** A bot or a scripted route that does not copy the designer's path. One number
that should move (objective health, hits on a volume).

**Steps.**
1. Play it yourself and note the number.
2. Run the bot three times.
3. If the number never moves, the content is decorative. Fix the cause, re-run three times.

**Fails when.** The bot uses the designer's route, so it hides the same miss.

**Validate.** Before/after logs of that number on three bot runs.

**Recover.** Do not add difficulty. Move the threat onto the objective the test measures.

**Skill.** `gamedev-game-testing`.
**Basis.** transcript.
**Src.** S14 L190-210.

---

## T-76 — Boss attacks are timelines

**Problem.** A boss with animations and a health bar still feels random or unfair,
because nothing tells the player when a hit can land.

**Why it works.** The source fight became readable with rules: no long gaps, not too
fast, never the same move three times, swing only if the player is in front, and a hurt
volume per move that is visible while it is active (S16).

**When.** A boss, elite, or one scripted duel. Not trash mobs.

**Inputs.** A move list. A dodge with a known iframe window.

**Steps.** See `gamedev-boss-encounter`. Authority is the data row (windup, active,
recovery), not the clip.

**Fails when.** Timings live only inside the animation, so a retarget silently changes
what is dangerous.

**Validate.** A 60 s log with no triple repeat, and every move dodged once from the
telegraph alone.

**Recover.** If dodges fail, lengthen windup or narrow the arc before adding particles.

**Skill.** `gamedev-boss-encounter`.
**Basis.** transcript.
**Src.** S16 L198-226.

---

## T-77 — Lock-on facing is a locomotion problem

**Problem.** Lock-on that turns the body 180° makes "step back" walk away from the fight.

**Why it works.** The source kept the character facing the boss while travelling backward
(S16).

**When.** A lock-on camera is in the spec.

**Inputs.** A move that separates facing from travel, or an authored backward-facing clip.

**Steps.**
1. While locked, facing stays on the target.
2. Backward input plays a backward walk, not a rotate-then-walk.
3. If the move set cannot do that, do not ship lock-on.

**Fails when.** The mesh faces away and the camera is the only thing locked.

**Validate.** Hold back for one second while locked: the chest still faces the boss, and
the root moves away.

**Recover.** Drop lock-on until the clip exists. A free camera is an acceptable ship.

**Skill.** `gamedev-boss-encounter`.
**Basis.** transcript.
**Src.** S16 L209-212.

---

## T-78 — Key poses, then in-betweens

**Problem.** A motion model given "make him swing" produces a plausible body and the wrong
silhouette (the source held a hammer like a boxer). Asking again rerolls the whole clip.

**Why it works.** Draw the stand, the swing, and the hit. Fit the skeleton to those poses
from front and side, then let the model fill the gaps (S16). A later failure (an arm on
the roar) was fixed on that joint only.

**When.** Combat or creature motion where the silhouette of the hit matters.

**Inputs.** Three poses. Joint limits (elbow one way, spine small, legs larger).

**Steps.**
1. Block the three poses.
2. Fill between them.
3. If one joint breaks, edit that curve.

**Fails when.** The generator also invents the timing of the hitbox. Hitboxes stay on
T-76's table.

**Validate.** The contact pose matches the reference in front and side views. Joints stay
inside the ranges in `gamedev-animation`.

**Recover.** Replace the pose, not the fight.

**Skill.** `gamedev-boss-encounter`, `gamedev-animation`.
**Basis.** transcript.
**Src.** S16 L131-143, L191-194.

---

## T-79 — A person picks sounds; the agent wires them

**Problem.** Games stay silent, or a model downloads a folder of clips that play at random.
The older transcripts only name the library (S01, S09). They never say when a sound fires.

**Why it works.** The later source: the director picked the sounds, including real
recordings for impacts, and the agent attached them (S14, S16). Music marked a mood
change, not every minute of play.

**When.** The loop is playable and feedback is missing or mushy.

**Inputs.** An event that already exists in gameplay. A file with a license.

**Steps.** See `gamedev-audio-wire`. No file without a manifest row. No playback without
that event's frame.

**Fails when.** Audio uses its own timer instead of the gameplay signal, so it drifts
off the hit-stop.

**Validate.** Mute test: name one decision (a dodge, a hit) that gets worse with sound off.
The manifest covers every file.

**Recover.** Delete sounds that do not change a decision. Add the missing signal in
gameplay before adding another file.

**Skill.** `gamedev-audio-wire`.
**Basis.** transcript+. The library name is from the transcripts. The manifest and the
mute test are engineering.
**Src.** S01 L359-362; S09 L99-101; S14 L190-192; S16 L25-29, L205-208, L223-224.

---

## T-80 — Market evidence before a build decision

**Problem.** Teams score ideas on excitement, then discover the verb already shipped.

**Why it works.** A verdict that separates observed store facts, inferences, and the
recommendation can be checked a week later. The evidence habits are adapted from Corey
Haines' marketingskills (MIT): date facts, do not treat a missing page as a missing
feature, do not invent buyer quotes, do not call likes demand.

**When.** Someone asks if a game should be built, priced, or changed. Not when the task
is one system inside a game that is already chosen.

**Inputs.** Web access. A one-sentence pitch. If the sentence cannot be written, four
questions (audience, session, verb, failure) and a stop.

**Steps.** See `gamedev-concept-judge`. Five dated competitor rows before any score.

**Fails when.** Search is skipped and the scores still appear. Those scores are void.

**Validate.** Every score tagged Observed or Inferred. A continue-number and a kill-number
for one cheap experiment.

**Recover.** If search is down, output "blocked", not a softer verdict.

**Skill.** `gamedev-concept-judge`.
**Basis.** engineering. Not from S01–S16. Attribution is in the skill's evidence reference.
**Src.** none.

---

## T-81 — Constraints, then five ideas, then one

**Problem.** "Give me ideas" produces a list of themes. None can be killed, because none
name a competitor.

**Why it works.** Questions first (team, time, engine, refusals, session, price). Then a
store scan of verbs. Then at most five loops plus one twist. Then one recommendation.
The others are not a backlog.

**When.** There is no chosen game.

**Inputs.** Answers to the six questions, or explicit assumptions written down.

**Steps.** See `gamedev-concept-lab`. Hand the winner to T-80 before production.

**Fails when.** Ideas are ranked by novelty, or a twist that is only art is allowed through.

**Validate.** The recommended concept cites a real complaint on a real game, with a URL
and a date.

**Recover.** If the scan finds three recent games with the same verb and no complaint you
can answer, do not pitch that verb.

**Skill.** `gamedev-concept-lab`.
**Basis.** engineering.
**Src.** none. Playing a greybox before art is T-74, which is transcript.
