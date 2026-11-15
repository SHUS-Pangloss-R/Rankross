# Mistakes

A chronological log of the things I got wrong in this repository.

I keep it because it is the part of my own record I actually learn from. Each
entry is: **what I believed -> what was true -> how I found out -> what it cost.**

Nothing here was caught by a crash. Every one of them produced a plausible-looking
number.

---

## 1. "100% accuracy means the model learned the shape" (2026-10-07)

**Believed:** the network had learned to recognise a bunny, an armadillo and a knot.
**True:** it had memorised the point distribution of those three specific meshes.
**Found by:** rotating the test cloud 90 degrees. It stopped recognising the object.
**Cost:** a week of numbers that meant nothing.
**Lesson:** accuracy on data generated from three shapes is not evidence of anything.
It was the first time I distrusted one of my own results, and it is the reason the
rest of this repository looks the way it does.

## 2. "92% is the accuracy ceiling of this setup" (2026-10-11)

**Believed:** with two Gaussians 0.173 apart and noise sigma 0.5, 92% was a
reasonable ceiling and the model had learned the "weak statistical pattern".
**True:** 92% is above what that setup can support. A single point cannot be
classified better than chance there, so the 92% was an artefact of evaluating on
the training distribution, not a ceiling.
**Found by:** re-deriving the Bayes bound instead of trusting the number.
**Cost:** one claim in `PointNetCloud_Practice/EXPERERIMENTS.md` that has to be
withdrawn.
**Lesson:** "the model learned the weak pattern" is the explanation you reach for
when you have not computed what the pattern is worth.

## 3. The A4 sheet was detected as a campus card (Day 1)

**Believed:** the reference object was found by its aspect ratio.
**True:** A4 has aspect 1.414, inside the +/-22% window around a card's 1.586, so the
detector locked onto the wrong object. Every length came out 10% short.
**Found by:** two independent scale estimates disagreeing.
**Lesson:** a tolerance wide enough to be robust is wide enough to match the wrong
thing.

## 4. Morphological opening ate 7 pixels of the cup (Day 1)

**Believed:** a 9x9 OPEN was a harmless cosmetic cleanup.
**True:** it eroded the silhouette. Body width 163 px -> 153 px, a 4.4% diameter
error, silently.
**Found by:** comparing against the ruler.
**Lesson:** **the bug that hurts is the one that does not crash.** See also
`Cup_Practice/README.md`.

## 5. "Detecting the base as a sudden width change works" (Day 1)

**Believed:** the contact shadow ends where the width stops growing fast, so I could
cut there.
**True:** on my data the largest sudden widening is at row 521 (`152 -> 158`), which
is the printed diamond pattern, not the base. The rule hit noise, produced 523 rows,
and I accepted it **because the resulting diameter matched the ruler**.
**Found by:** plotting the width profile and looking at where it actually bends.
**Cost:** Day 1 was reported as "PASS" on the strength of a number I had selected.
**Lesson:** accepting a result because it matches is the same as tuning it to match.

## 6. "Three independent measurements agree within 1.2%" (Day 1)

**Believed:** height, max diameter and base diameter were three independent checks.
**True:** the height check is an identity (`scale = 213 / rows`, so `rows * scale`
is 213 for any data), and the two diameters share the same fitted base row. Only the
scale-free ratio carried information: 1.063 against the ruler's 1.048, i.e. 1.4%.
**Found by:** tracing where each number came from instead of reading the final table.
**Cost:** the "PASS" that Day 2 then had to withdraw.
**Lesson:** before quoting an agreement, ask which quantity both sides computed
*without* the fitted parameter.

## 7. "The shadow is 54 rows" (Day 2)

**Believed:** subtracting the shadow would need about 54 rows cut off.
**True:** the tail is about 7 mm, roughly 19 rows. The 54 came from assuming the
ruler's 65 mm was right and solving backwards for it.
**Found by:** plotting `r(z)` and looking at where the profile becomes vertical.
**Lesson:** a number obtained by solving backwards for it is not a measurement.

## 8. `width = [r-1+1 for l, r in ...]` (T1)

**Believed:** I was computing the width of each row.
**True:** `r - 1 + 1` is just `r`, so the "width" was the x coordinate of the right
edge (248 px). The real max width was 162.
**Found by:** the number was not plausible as a width for a 65 mm cup.
**Lesson:** a variable named `width` that is not a width will still run.

## 9. The yaw experiment that could not fail (Day 3)

**Believed:** rotating the cup 30 degrees about its vertical axis was a fair test of
pose robustness. The unaugmented model scored 0.9946 and looked robust.
**True:** the labels are height bands, and a yaw rotation leaves height unchanged, so
the test had nothing to fail at. It was a null experiment.
**Found by:** asking what a failure would even look like, after the fact.
**Cost:** one day. The corrected version (tilt) gives a 62.3% drop.
**Lesson:** **a test is only worth running if I can say in advance what failing looks
like.**

## 10. `pcd2` never received the transformed points (T8)

**Believed:** I had built a target cloud transformed by a known rotation and
translation, so I could measure registration error against the truth.
**True:** I computed the transformed points into a new array `P2`, added the noise to
`P2`, and then re-assigned `pcd2` from `voxel_down_sample` of the **original**
points. Every downstream number was computed against a target that had never moved.
**Found by:** the two clouds' centroids should have differed by the known translation
and did not.
**Cost:** the whole of T8's first conclusion. The reported 61.7 degree error was
mostly this bug; after the fix it is 23.07 degrees, and the remainder is the
unobservable spin.
**Lesson:** **transform-then-assign is two steps and I only did one.** This is the
same class as #4: no exception, just a wrong number.

## 11. Reading a stale variable after a loop (T9)

**Believed:** the ICP result I was evaluating was the one from the delta=0 start.
**True:** `res_icp` had been overwritten by the last iteration of the loop
(delta=180, the case that fails completely), so the evaluation printed 0.00% and
0.0000 mm.
**Found by:** the picture and the numbers disagreeing.
**Lesson:** `for` has no block scope in Python. Store per-iteration results in a
dict, or the loop variable outlives the loop.

## 12. The axis error was computed from the wrong matrix (T8/T9)

**Believed:** the 0.0 degree axis error was evidence that the registration had found
the right orientation.
**True:** it was computed from `R_est`, which belonged to an earlier RANSAC run on a
copy of the *same* point cloud. That comparison is trivially 0. The ICP result was in
`R_est_icp`.
**Found by:** noticing that a number which should depend on the run did not change
between runs.
**Lesson:** when a number is exactly 0.0 or exactly 1.0, check which variable it
actually came from.

---

## What the twelve have in common

- **None of them crashed.** Each produced a number that looked fine.
- **Each was found by comparing two numbers that should have agreed** -- never by
  looking at a picture alone. The two exceptions (#1 and #9) were found by asking
  what the experiment could not detect.
- **The dangerous ones are the ones that make the result look good** (#5, #6).
  A bug that makes the answer wrong is annoying; a bug that makes the answer right
  for the wrong reason is worse, because you stop looking.

## The rule I now use

Before quoting any agreement between two numbers, ask:

> Which quantity did both sides compute *without* the parameter I fitted?

If the answer is "none", the agreement is not a check.
