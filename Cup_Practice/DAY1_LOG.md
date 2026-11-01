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

| Check | Photo-derived | Ruler | Error | |
| :--- | ---: | ---: | ---: | :--- |
| Height | 212.59 mm | 213 mm | -0.19% | PASS |
| Max diameter | 65.16 mm | 65 mm | +0.25% | PASS |
| Base diameter | 61.29 mm | 62 mm | -1.14% | PASS |

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
   book, so its silhouette fades into a shadow that tapers over ~54 rows. That
   made the object look 22 mm taller, and because the height is the scale anchor,
   it also inflated the diameter. Fixed by detecting the base edge as the point
   where the width stops growing fast, rather than by any fraction of the global
   width. A fraction rule was tried first and it wrongly trimmed the synthetic
   frustum, whose base is legitimately its narrowest part.

Diagnostic that nailed it: the silhouette's aspect ratio was 577/163 = 3.54,
while the ruler's was 213/65 = 3.28. The 8% gap could not be explained by
perspective (perspective shrinks height, it does not stretch it), so it had to be
extra rows in the mask. After the fix the ratio is 523/160 = 3.27.

##  Conclusion

**The `silhouette = profile` assumption holds for this object.** Three
independent measurements agree within 1.2%, and the two volumes (spline and
frustum) agree within 0.3%, which is what a nearly-straight-walled thermos
should do.

What I actually learned from this step, in order of surprise:

- **The bug that hurts is the one that does not crash.** Opening the mask was a
  one-line cosmetic cleanup; it cost 4.4% of the diameter.
- **Two measurements beat one, always.** Every failure above was found because
  two independent numbers were compared, never because a picture looked wrong.
- **The anchor is a choice, not a fact.** Anchoring on height makes the height
  check trivially true and pushes the error into the diameters. That is fine only
  because the diameters are independent readings.

##  Open issues

- **No capacity measurement, so no density check.** The thermos has a lid and a
  vacuum liner, so filling it is awkward anyway. Accepted for now; the diameter
  agreement is a weaker but sufficient substitute. To be revisited if a scale or
  syringe shows up.
- **This is one object.** Nothing here generalises until a second cup is measured
  the same way.
- **The base cut is tuned to a flat-bottomed body.** A bowl-shaped object would
  be trimmed wrongly; the function documents this.
