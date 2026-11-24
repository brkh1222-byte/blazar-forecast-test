# DRAFT email to the Peñil et al. group — NOT SENT

> Status: draft only. Nobody has been contacted. The researcher decides whether, when and in
> what words to send it. Revised 2026-11-25 (session 2): updated to the piloting policy, and
> made the questions more specific now that Part B has been run.
> Check before sending: the corresponding author's current address on the MNRAS paper
> (doi:10.1093/mnras/stag1141); whether to attach the draft note; the sender block.

**To:** Dr. Pablo Peñil (corresponding author)
**Cc:** [co-authors / mentor — TBD]
**Subject:** Question about the forecast check in Sec. 8.1 of your 2026 MNRAS paper (stag1141)

Dear Dr. Peñil,

I am writing about your paper "Gamma-ray periodicity in jetted AGNs: revisiting periodicity
candidates with >17 years of Fermi-LAT data" (MNRAS 550, stag1141; arXiv:2606.15676). I am
comparing the forecast result in Section 8 (19 of 59 predicted high states supported) with
chance baselines from randomly shifted forecasts and red-noise simulations, and I would like to
reproduce your scoring exactly before I draw any conclusion.

From Section 8.1 I understand that
- the window is [t_pred − W, t_pred + W] with W = 0.20 T;
- the observed peak is the maximum flux in that window, at t_obs;
- a forecast is compatible if |t_obs − t_pred| ≤ max(60 d, 0.20 T).

Read literally, every evaluable forecast would be compatible, because t_obs always lies inside
the window. Since 40 of the 59 forecasts are marked as not supported, I believe I am missing a
step. I tried four simple guesses on Light Curve Repository data (maximum not at the window
edge; a local maximum; a flux threshold; the maximum of the whole cycle within the tolerance).
The best of them agrees with Table A7 for only 40 of 59 forecasts (Cohen's κ = 0.34), so I
cannot reproduce your verdicts. Could you tell me:

1. What additional condition decides that a forecast is not supported? (For example a flux
   threshold defining a "high state", or a search window wider than 0.20 T.)
2. The period T and the reference epoch used for each source in Table A7, in particular for the
   sources with a single forecast.
3. The end date of the light curves used for Table A7, and whether they are the public LCR
   light curves (30-day bins, fixed index, TS ≥ 4) without further processing.
4. Whether you would be willing to share the script, or the list of t_obs values, used for
   Section 8.1.

My preliminary finding is that the chance hit rate depends strongly on the exact rule (roughly
30% to 80% for the rules I tried), which is why the exact rule matters. I would be glad to send
you the draft and the code before posting anything, and I will of course acknowledge your help.

I have also written down in advance how I will score the new forecasts of your Table 3 as the
data arrive, and I am happy to share that plan as well.

Thank you for your time.

Best regards,
[NAME — TBD]
[affiliation / "independent researcher" — TBD]

[AI-USE STATEMENT — TBD: if the paper discloses AI assistance, consider one sentence here too,
e.g. "The analysis code and draft were prepared with an AI assistant and are being checked by me."]
