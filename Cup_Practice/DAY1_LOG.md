# Day 1 Log: Does the Photo Pipeline Reproduce the Ruler?

##  Motivation

Before modelling anything I wanted one number that could tell me whether the
whole chain (photo -> silhouette -> profile -> volume) is trustworthy. The plan
was to weigh the water capacity and derive the material density, but that needs
a scale or a measuring jug, and the dorm has neither.

So the check was restructured: **anchor the absolute scale on the ruler-measured
height**, then use the two diameter readings as the independent test. If the
silhouette's aspect ratio matches the ruler's aspect ratio, the segmentation is
right; if it does not, something in the mask is wrong.

##  Capture

- Thermос standing on a book, dark chair backrest behind it.
- Phone held level at the cup's mid-height, ~50 cm away, 1x, focus locked.
- Two frames only: cup present, cup absent. Same camera position.
- In the end **no reference object was used at all**: the campus card was tried
  first, but it leans against the backrest, and the tilt squashed its aspect
  ratio from 1.586 to 1.87, which silently corrupts any scale derived from it.

Ground truth, measured with the campus card (85.60 mm long edge) as a ruler:

| Quantity | Value |
| :--- | :--- |
| Total height (to lid top) | 213 mm |
| Max body diameter | 65 mm |
| Base diameter | 62 mm |

##  Result

```
scale      : 0.40727 mm/px  (anchored on ruler height, 213.0 mm / 523 px)
height     : 212.59 mm
max_dia    :  65.16 mm
base dia   :  61.29 mm
V spline   : 626.54 ml
V frustum  : 624.52 ml
```

| Check | Photo-derived | Ruler | Error | Status |
| :--- | ---: | ---: | ---: | :--- |
| Height | 212.59 mm | 213 mm | -0.19% | **circular** |
| Max diameter | 65.16 mm | 65 mm | +0.25% | depends on the cut |
| Base diameter | 61.29 mm | 62 mm | -1.14% | depends on the cut |

**Correction (added on Day 2, after the check was re-examined).** These three are
not independent readings, and the PASS labels they originally carried were wrong.

- The height error is an identity: `scale = 213 / 523`, so `523 x scale = 213` for
  any data. It cannot fail.
- Both diameters are multiplied by the same `scale`, and `scale` depends on where
  the base row is placed. At 523 rows the diameter is 65.16; at 577 rows it is
  59.06. The value 523 was the one the rule happened to return, and I accepted it
  because the result matched. That is selection by outcome, not a test.
- The only scale-free check is the **ratio** of the two widths:
  `160 / 150.5 = 1.063` against the ruler's `65 / 62 = 1.048`, agreeing to 1.4%.
  That is a real check, and it tests the *shape*, not the size.

So the honest statement for this table is: shape consistent to 1.4%, absolute
scale unverified. See `DAY2_LOG.md` for why a single photo cannot resolve it.

##  Analysis: three bugs, and what caught each

The pipeline did not work first time. All three failures were caught by the same
thing, a number disagreeing with another number.

1. **The card was detected as an A4 sheet.** The reference mode accepted any
   contour within 22% of a card's 1.586 aspect ratio, and A4 is 1.414, which is
   inside that window. Every length came out ~10% short. Fixed by choosing the
   reference mode from the reference size instead of always trying card mode.

2. **Morphological opening eroded the silhouette by 7 px.** The cup body is
   163 px wide and the mask reported 153, a 4.4% diameter error, with no warning
   of any kind. Fixed by shrinking the OPEN kernel to 3x3. This is the same class
   of bug as the pooling axis in PointNet: a single parameter that silently
   changes the answer without crashing.

3. **The contact shadow was being read as part of the cup.** The cup stands on a
   book, so its silhouette fades into a shadow. First attempt: detect the base as
   the point where the width stops growing fast. That gave 523 rows and a diameter
   matching the ruler, so I called it fixed.

   **It was not fixed.** On Day 2 I went back to the width profile: the largest
   sudden widening in the bottom 12% is at row index 521 (`152 -> 158`), which is
   the printed pattern on the cup, not the base. The rule hit noise and produced a
   number I then accepted. A fraction-of-global-width rule was also tried and it
   wrongly trimmed the synthetic frustum, whose base is legitimately its narrowest
   part.

Diagnostic that started this: the silhouette's aspect ratio was 577/163 = 3.54,
while the ruler's was 213/65 = 3.28. The 8% gap could not be explained by
perspective (perspective shrinks height, it does not stretch it), so it had to be
extra rows in the mask. What Day 1 did not establish was **which** extra rows to
remove; 523/160 = 3.27 matches the ruler by construction once 523 is chosen.

##  Conclusion

**The `silhouette = profile` assumption holds for this object. The absolute scale
does not follow from it.** The scale-free check, the ratio of max to base width,
agrees to 1.4%; the spline and frustum volumes agree within 0.3%. Everything that
depends on *where the base row is* is unverified, and Day 2 showed the size of
that hole: 9% on the diameter, with no way to close it from one photo.

What I actually learned from this step, in order of surprise:

- **The bug that hurts is the one that does not crash.** Opening the mask was a
  one-line cosmetic cleanup; it cost 4.4% of the diameter.
- **Two measurements beat one, always.** Every failure above was found because
  two numbers were compared, never because a picture looked wrong.
- **A matching number is not automatically a check.** I had three numbers that
  agreed and only one of them carried information, because the other two shared a
  parameter I had quietly chosen. The rule I now use: before quoting an agreement,
  ask which quantity both sides computed *without* the fitted parameter.
- **The anchor is a choice, not a fact.** Anchoring on height makes the height
  check trivially true and pushes all the error into the diameters. That would be
  acceptable only if the diameters were independent of the anchor, and they are
  not: both depend on where the base row is placed.

##  Open issues

- **No capacity measurement, so no density check.** The thermos has a lid and a
  vacuum liner, so filling it is awkward anyway. Accepted for now; the diameter
  agreement is a weaker but sufficient substitute. To be revisited if a scale or
  syringe shows up.
- **This is one object.** Nothing here generalises until a second cup is measured
  the same way.
- **The base cut is tuned to a flat-bottomed body.** A bowl-shaped object would
  be trimmed wrongly; the function documents this.
