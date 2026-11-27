---
title: Measuring Cognitive Hollowing: A Study Design for Unassisted Skill After AI Adoption
short: Measuring Cognitive Hollowing
kind: Research proposal, version 1.0, November 2026
date: November 2026
published: 2026-11-27
place: research
summary: Professionals in several fields complete standardized tasks with the AI switched off, before AI adoption and at intervals of up to two years afterwards.
pdf: measuring-cognitive-hollowing.pdf
orcid: https://orcid.org/0009-0000-1700-0435
---

## Abstract

Short experiments now show that AI assistance can lower people’s performance once the AI is removed, and one clinical study suggests the same may happen in professional practice. What is missing is evidence about practicing professionals over years, across professions, and about whether the loss can be reversed. This proposal sets out a field study to supply it. Professionals in several fields complete standardized tasks with the AI switched off, before AI adoption and at intervals of up to two years afterwards. Where organizations are rolling out AI anyway, the order of rollout is randomized. The design adds three arms: a comparison of trainees who learned before and alongside AI, a randomized test of periodic AI-off drills as a way to reverse loss, and a randomized test of thinking first and using AI second. Sample sizes are worked out from the effect seen in the clinical study. Each hypothesis is stated with the result that would count against it. The study would measure directly the condition that earlier work identified as the main lever against deep dependence on AI.

**Keywords:** deskilling; AI assistance; unassisted performance; skill formation; field experiment; stepped-wedge design; automation; human oversight

**Suggested citation:** Potvin, J. (2026). *Measuring Cognitive Hollowing: A Study Design for Unassisted Skill After AI Adoption.* Research proposal, version 1.0, November 2026.

## 1. Motivation

In earlier work I argued that the loss of independent human capability, which I called hollowing, is the condition humans control most directly in any long-term dependence on AI, and so the main lever against it (Potvin 2026). That paper proposed measuring unassisted performance as an early warning sign. This proposal sets out how.

**What is already known.**

- **Clinical practice.** At four Polish endoscopy centres, the rate at which doctors detected precancerous growths in colonoscopies done without AI fell from 28.4% before the centres introduced AI to 22.4% after (Budzyń et al. 2025). The study is observational.
- **Education.** In a field experiment with nearly 1,000 high school mathematics students, unrestricted access to a generative AI tutor improved practice performance, but when access was removed, students did worse on an exam than students who never had access (Bastani et al. 2025). A tutor with guardrails largely avoided the harm.
- **Software engineering.** In a randomized experiment, 52 mostly junior developers learned a new programming library with or without AI. The AI group scored 50% on a follow-up quiz against 67% for the group that coded by hand (Shen and Tamkin 2026). How participants used the AI mattered.
- **Brief assistance.** Across randomized experiments with 1,222 participants in mathematics and reading, about ten minutes of AI assistance improved performance while the AI was present but reduced persistence and performance once it was removed (Liu et al. 2026).
- **Aviation.** Pilots’ manual control skills were largely retained despite heavy use of automation, but the cognitive skills needed for manual flight, such as keeping track of position, were weaker (Casner et al. 2014). This matches the older observation that automation leaves operators without practice in the skills they need when automation fails (Bainbridge 1983).
- **Measurement.** Fan (2026) argues that current measurement shows where AI is used and whether it helps immediate tasks, but not whether people become more capable of working independently. That paper proposes linking usage records to independent tests of unassisted performance while varying the kind of help the AI gives. Not every experiment finds harm; Fan (2026) reviews mixed results.

**The gap.** The experiments are short and mostly involve students or novices. The one study of practicing professionals is observational and covers one skill. There is no long-term field study, across professions, of practicing professionals’ unassisted performance, of whether trainees who learn alongside AI reach the same level, and of whether any loss can be reversed.

## 2. Questions

1. Does unassisted performance of practicing professionals fall after AI adoption, and does the fall grow with the amount of AI use?
2. Does the order of use, thinking first and using AI second, reduce the fall?
3. Do trainees who learn alongside AI reach the same unassisted level as trainees who learned before AI, at the same stage of training?
4. Can a fall be reversed by periodic practice with the AI switched off?
5. Which skills are most affected: procedural skills, or the cognitive skills of judging, diagnosing and checking?

## 3. Design

### 3.1 Settings

Four to six professions in which unassisted performance can be scored objectively and AI is being adopted: for example, colonoscopy or radiology, software engineering, translation or professional writing, auditing, and legal issue spotting.

### 3.2 Main design (Question 1)

- **Where organizations are rolling out AI anyway:** a stepped-wedge cluster design, in which sites or teams adopt AI in a randomly assigned order. Every site eventually adopts, but the timing is random, which allows causal comparison.
- **Where randomizing the order is not possible:** a matched difference-in-differences design, comparing adopting sites with similar sites that have not yet adopted.
- **AI-off assessments** at baseline and at 6, 12 and 24 months after adoption. Assessments use standardized simulated tasks, not live work, and are scored by raters who do not know the participant’s group.
- **Assisted performance** is measured at the same points, so that the net value of AI is reported alongside any loss.
- **Usage records**, collected with consent, give the amount of AI use, its mode (answers, hints or checking) and its order within each task.

### 3.3 Additional arms

- **Learner cohorts (Question 3).** Trainees in the same programs who trained before AI and alongside AI take the same unassisted test at the same stage, with adjustment for differences between cohorts.
- **Reversibility (Question 4).** Within adopting sites, teams are randomized to periodic AI-off drills or none, and their trajectories are compared.
- **Order of use (Question 2).** Within adopting sites, teams are randomized to guidance to draft first and use AI second, or to no guidance.

### 3.4 Outcomes

- **Primary:** change from baseline in the profession-specific standardized unassisted score.
- **Secondary:** persistence (time before giving up, or the rate of skipped items, following Liu et al. 2026); accuracy of people’s own estimates of their unassisted skill; assisted performance; and the ability to detect errors in AI output, the skill needed to oversee AI.

## 4. Sample size

These figures are illustrations, worked out in code, for planning. They use a two-sided test at the 5% level with 80% power.

- **Binary outcomes, using the clinical effect.** To detect a fall in a detection rate from 28.4% to 22.4%, the size of the change in Budzyń et al. (2025), requires about **826 procedures per group** before allowing for clustering.
- **Clustering.** Procedures are grouped within clinicians. With an assumed intraclass correlation of 0.05 and 50 procedures per clinician, the design effect is 3.45, giving about **2,850 procedures per group**. With 0.02 and 20 per clinician, it is about 1,140. The real correlation must be estimated in a pilot.
- **Continuous scores.** To detect a standardized difference of 0.3 between groups requires about **176 participants per group** before clustering, and about 340 with a design effect of 1.95.

## 5. Hypotheses, and what would count against them

| # | Hypothesis | Result that would count against it |
|---|---|---|
| H1 | Unassisted performance falls after AI adoption, compared with sites that have not yet adopted | No fall beyond the confidence interval at 12 and 24 months |
| H2 | The fall grows with the amount of AI use | No relation between use and change |
| H3 | Drafting first and using AI second reduces the fall | No difference between guidance arms |
| H4 | Trainees who learned alongside AI score lower unassisted than earlier cohorts at the same stage | No difference after adjustment |
| H5 | Periodic AI-off drills reverse or prevent the fall | No difference between drill arms |
| H6 | Cognitive skills (judging, diagnosing, checking) fall more than procedural skills | Similar or smaller falls in cognitive skills |

**Why a null result matters.** If H1 fails across professions over 24 months, the hollowing condition is not being met at the scale assumed in Potvin (2026), and the claim that it is the main near-term risk should be weakened accordingly.

## 6. Analysis plan

- Hypotheses, outcomes and analyses are preregistered before data collection.
- Stepped-wedge data are analysed with mixed-effects models that include time and site effects; difference-in-differences data with event-study models that test for differing trends before adoption.
- The relation between use and change is estimated with the usage records, and differences by experience level are reported separately, because the experimental studies found the largest effects among novices.
- Corrections for multiple comparisons across professions and hypotheses.

## 7. Ethics

- **No AI is withheld from live patient care or other live work.** AI-off assessments use simulated cases or retrospective material.
- **Individual results stay confidential.** Assessment results are not shared with employers in a form that identifies individuals, so that taking part cannot harm anyone’s job.
- **Consent and data protection** for usage records, with collection limited to what the analysis needs.

## 8. Related work, and what is new

**Credited prior work.** The clinical observation of Budzyń et al. (2025); the experiments of Bastani et al. (2025), Shen and Tamkin (2026) and Liu et al. (2026); the aviation evidence of Casner et al. (2014) and the analysis of Bainbridge (1983); and the measurement program of Fan (2026), which already distinguishes the stock of existing skill from the formation of new skill and proposes linking usage records to unassisted tests. The framing of hollowing as a strategic indicator comes from Potvin (2026).

**What appears to be new.**

1. A long-term field design, across several professions, that tracks practicing professionals’ unassisted performance at repeated intervals as an early warning indicator.
2. Measuring the loss of existing skill and the failure to form new skill in the same study and the same professions.
3. A randomized test of whether periodic AI-off drills reverse a measured loss.
4. A randomized test, in professional settings, of the order-of-use effect first seen in a small laboratory study (Kosmyna et al. 2025).

Searches covered deskilling after AI adoption, randomized trials of unassisted performance, skill formation with AI, and automation and manual skills. They were not exhaustive.

## Appendix A. How each claim stands

| # | Claim | Kind | Basis | Status |
|---|---|---|---|---|
| 1 | Brief AI assistance can lower performance once the AI is removed | Evidence | Liu et al. (2026); Bastani et al. (2025); Shen and Tamkin (2026) | Checked; mostly short experiments with students or novices |
| 2 | Professional skill may fall after AI adoption | Evidence | Budzyń et al. (2025) | Checked; observational, one skill |
| 3 | Cognitive skills are more exposed than procedural ones under automation | Evidence | Casner et al. (2014) | Checked; aviation |
| 4 | No long-term, multi-profession field study of unassisted skill exists | Open | Searches in Section 8 | Not found; searches not exhaustive |
| 5 | About 826 procedures per group detect a fall from 28.4% to 22.4% | Logic (calculation) | Standard formula for two proportions | Holds, before clustering |
| 6 | Hollowing at scale (H1) | Open | This study | Not yet tested |

## References

Bainbridge, L. (1983). Ironies of Automation. *Automatica* 19(6), 775 to 779. https://doi.org/10.1016/0005-1098(83)90046-8

Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö. and Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *Proceedings of the National Academy of Sciences* 122(26), e2422633122. https://doi.org/10.1073/pnas.2422633122

Budzyń, K. et al. (2025). Endoscopist deskilling risk after exposure to artificial intelligence in colonoscopy: a multicentre, observational study. *Lancet Gastroenterology and Hepatology* 10(10), 896 to 903. https://doi.org/10.1016/S2468-1253(25)00133-5

Casner, S. M., Geven, R. W., Recker, M. P. and Schooler, J. W. (2014). The Retention of Manual Flying Skills in the Automated Cockpit. *Human Factors* 56(8), 1506 to 1516. https://doi.org/10.1177/0018720814535628

Fan, A. X. (2026). Toward Measuring AI’s Effects on Skill Formation: The Stock-Formation Gap. arXiv:2605.16283.

Kosmyna, N. et al. (2025). Your Brain on ChatGPT: Accumulation of Cognitive Debt when Using an AI Assistant for Essay Writing Task. arXiv:2506.08872.

Liu, G., Christian, B., Dumbalska, T., Bakker, M. A. and Dubey, R. (2026). AI Assistance Reduces Persistence and Hurts Independent Performance. arXiv:2604.04721.

Potvin, J. (2026). [*Offshoring the Mind: AI Dependence, Lost Capability and the Risk of a Cold Standoff Between Humans and AI.*](/essays/offshoring-the-mind/) Version 1.0, November 2026.

Shen, J. H. and Tamkin, A. (2026). How AI Impacts Skill Formation. arXiv:2601.20245.
