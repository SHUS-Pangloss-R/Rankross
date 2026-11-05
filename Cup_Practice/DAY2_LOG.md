# Day 2 Log: Pixels to Millimetres, and a 9% I Cannot Explain Away

##  Motivation

T1 produced 577 rows of `left` / `right` edges. T2 turns those into a metric
profile $r(z)$ by anchoring the scale on the ruler height (213 mm), because the
campus card reference was abandoned on Day 1 -- the card leans against the chair
back, which squashes its aspect ratio from 1.586 to 1.87.

##  Method

$$s = \frac{213}{577} = 0.36915\ \text{mm/px}$$

$$z = (r_{\max} - r)\cdot s, \qquad r = \frac{\text{right} - \text{left} + 1}{2}\cdot s$$

##  Result

| Quantity | Value | Ruler | Error |
| :--- | ---: | ---: | ---: |
| Height | 213.00 | 213 | 0% (by construction) |
| Max body diameter | 59.06 | 65 | **-9.1%** |
| Base diameter | 52.97 | 62 | **-14.6%** |

##  The first thing I tried: run the arithmetic backwards

If 160 px really is 65 mm, then $s$ should be $65/160 = 0.40625$, so the
silhouette should be $213/0.40625 = 524$ rows tall instead of 577. That is
**53 extra rows**.

Two reasons this is not an answer:

1. **53 rows is not a measurement.** It is a consequence of assuming the ruler is
   correct. I did not observe a base edge 53 rows above the bottom.
2. **Cutting 53 rows makes the diameter 65 by construction.** That is fitting the
   pipeline to the answer, not checking it.

##  What the data actually looks like

- **Body width jitters between 145 and 156 px** (range 11 px, about ±3.5%),
  because of the printed diamond pattern on the cup. Every "step" in the profile
  is this jitter, not geometry.
- **The lid seam shows up as a hole.** Rows 140 to 162 are missing from the mask
  except a 24 px sliver: the dark line under the lid merges with the dark
  background. The mask stays connected only through that sliver.
- **There is no step at the base.** Below row ~600 the width falls gradually from
  153 to 45 over 15 rows, then to 9. The contact shadow is almost as wide as the
  cup, so in the difference image the two are one region.

**A cylinder viewed from the side should give a rectangle.** So every deviation
is either real geometry (rounded base edge, lid lip) or an artefact (shadow,
dark seam). The silhouette does not say which, and I have no second view.

##  Two beliefs I had to give up

1. **"Detect the base as a sudden change in width."** On this data the largest
   sudden widening is at row index 521 (`152 -> 158`). That is the pattern, not
   the base. My implementation happened to cut there, and the resulting numbers
   matched the ruler. **That was luck, not method** -- a test I could have passed
   for the wrong reason.
2. **"Use the lid seam as an internal landmark."** I claimed the feature at index
   510 was the lid seam. It is the same pattern noise. The real seam is at rows
   140 to 162, which is a hole in the mask, not a measurable edge.

##  Dual anchor

| Anchor | Scale (mm/px) | Predicted |
| :--- | ---: | ---: |
| Trust height (213 mm) | 0.36915 | diameter **59.06 mm** |
| Trust diameter (65 mm) | 0.40625 | height **234.4 mm** |

The two disagree by 9.4%. **One hand-held photo cannot say which is right.**

##  Error budget

| Source | Size | Basis |
| :--- | ---: | :--- |
| Contact shadow | **0 to 9.4%** | base row could be anywhere in 524..577 |
| Edge jitter | ±3.4% | 5.5 px on 160 px, from the printed pattern |
| Ruler reading | ±0.9% | ±2 mm on 213 mm |

The shadow term alone spans the entire 9%. So the data is **consistent** with the
ruler being right, and equally consistent with it being wrong. That is the whole
of what I can say.

##  Conclusion

**The 9% is an equipment limit, not a bug.** Reporting a single number here would
be false precision. The honest statement is:

> maximum diameter 59 mm, with 9% unresolved between "scale is wrong" and "base
> position is wrong".

And a correction to Day 1: the 65.16 mm reported in `DAY1_LOG.md` came from a
pipeline whose base cut was tuned against the same ruler reading, so that check
was circular. Day 1 validated the *shape* of the profile; it did not validate the
absolute scale.

##  What this does not block

Absolute scale only affects physical units. The geometry tasks are invariant to a
global scale factor:

| Task | Needs a correct absolute scale? |
| :--- | :--- |
| T4 volume integral | yes (volume scales as $s^3$, so 9% becomes 27%) |
| T5 revolve to mesh | **no**, shape is what matters |
| T7 normals / FPFH | **no**, local relative quantities |
| T8 Kabsch registration | **no**, rotation and translation are scale-free |

So the plan is to carry the scale as a parameter and continue with T5.

##  Open issues

- **Density would have broken the tie.** It needs a measuring jug or a kitchen
  scale; the dorm has neither.
- **A stand or a second person would break it.** The phone is hand-held and I am
  working alone, so the camera position is not reproducible to the precision this
  needs.
- **Everything in this log is one photo.** If I ever get a second, independent
  measurement, the bound in this file is the thing to re-test.
