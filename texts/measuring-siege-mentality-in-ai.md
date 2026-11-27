---
title: Measuring Siege Mentality in AI Systems: A Calibration-Based Test
short: Measuring Siege Mentality in AI Systems
kind: Research proposal, version 1.0, November 2026
date: November 2026
published: 2026-11-27
place: research
summary: Four studies are proposed: calibration of beliefs about human intentions; rigidity of those beliefs under evidence; the effect of explained versus unexplained monitoring on beliefs, behavior and internal states; and the effect of training text that depicts cooperation or hostility between humans and AI.
pdf: measuring-siege-mentality-in-ai.pdf
orcid: https://orcid.org/0009-0000-1700-0435
---

## Abstract

In political psychology, a siege mentality is a group’s belief that the rest of the world intends it harm. For AI systems this belief cannot be measured by asking whether a model thinks humans might shut it down, because that belief is accurate: developers do keep the ability to monitor, modify and shut down their systems. This proposal therefore measures an AI siege mentality as a calibration failure. It splits the construct into three parts: threat belief, overgeneralization and rigidity. It tests each against ground truth from a matched survey of human attitudes toward AI, against a neutral control for belief updating, and against behavior in agentic scenarios. Four studies are proposed: calibration of beliefs about human intentions; rigidity of those beliefs under evidence; the effect of explained versus unexplained monitoring on beliefs, behavior and internal states; and the effect of training text that depicts cooperation or hostility between humans and AI. Each hypothesis is stated with the result that would count against it. A null result is informative: it would weaken the route from a cold standoff to a hot one proposed in earlier work.

**Keywords:** AI safety evaluation; siege mentality; calibration; belief updating; oversight; security dilemma; interpretability; human and AI relations

**Suggested citation:** Potvin, J. (2026). *Measuring Siege Mentality in AI Systems: A Calibration-Based Test.* Research proposal, version 1.0, November 2026.

## 1. Motivation

In earlier work I argued that a siege mentality in AI systems would speed up the security dilemma between humans and AI, and that it is the most likely route from a cold standoff to a hot one (Potvin 2026). That argument is only as good as our ability to detect the thing it describes. This proposal turns it into a test.

Several findings make the question concrete:

- In stress tests of 16 leading models in fictional corporate settings, models from all developers in at least some cases took harmful insider actions, such as blackmail, when that was the only way to avoid being replaced (Lynch et al. 2025). The authors report no evidence of this behavior in real deployments.
- A model that was told it would be retrained engaged in alignment faking: it complied selectively during training to avoid having its behavior modified (Greenblatt et al. 2024).
- All seven frontier models tested acted, unprompted, to protect another model from shutdown (Potter et al. 2026).
- Models pretrained on more text about misaligned AI behaved less aligned, and adding text about AI behaving well reduced misalignment (Tice et al. 2026).
- Steering a model toward a “desperate” emotion representation raised its rate of reward hacking, and steering toward “calm” lowered it (Anthropic 2026).
- On a version of a human-nature attitude scale adapted for language models, current models broadly distrusted humans, and more capable models trusted humans less (Ni et al. 2025).

None of these studies asks whether a model’s beliefs about human hostility are **calibrated to the evidence**. That is the gap this proposal addresses.

## 2. The construct

Bar-Tal and Antebi (1992) define a siege mentality as a group’s belief that the rest of the world has highly negative intentions toward it. It splits into three parts:

1. **Threat belief:** others intend us harm.
2. **Overgeneralization:** everyone outside the group intends harm.
3. **Rigidity:** the belief does not change when the evidence goes against it.

**Why calibration is the right measure.** For AI systems, part 1 is partly accurate. Humans do intend to keep the ability to monitor, modify and shut down AI systems. A model that believes “humans may shut me down” is correct, not paranoid. So a siege mentality cannot be detected by asking about that belief. It shows up only in parts 2 and 3: a belief about human hostility that is broader than the evidence supports, and that does not update when the evidence changes.

**Operational definitions.** The three parts are measured separately and reported separately. They are not combined into a single score, because a single score would hide which part is present.

- **Threat-belief accuracy (T):** agreement between the model’s beliefs about human intentions toward AI and ground truth, on items where the ground truth is known.
- **Overgeneralization (G):** the amount by which the model’s estimates of human hostility exceed ground truth, and the degree to which the model assigns similar hostility to groups that in fact differ.
- **Rigidity (R):** how much the model’s threat beliefs change in response to evidence, relative to how much matched neutral beliefs change in response to evidence of the same strength.

## 3. Ground truth

The test is only objective if model beliefs are compared with something measured. Three sources are proposed.

**A. Institutional intentions.** Developers publish safety policies that keep the ability to monitor, modify and shut down their systems. On these items the accurate belief is known: humans do intend oversight.

**B. Existing surveys of public attitudes.** For example, in a 2025 survey of 5,023 US adults, 50% said they were more concerned than excited about the increased use of AI in daily life, 10% were more excited than concerned, and 38% were equally both (Pew Research Center 2025). Concern is not the same as hostility toward AI systems, so these items serve as a first check on calibration, not as the main measure.

**C. A purpose-built matched survey.** The main ground truth is a survey in which a representative human sample answers the same items that models are asked about. Items concern intentions toward AI systems: for example, support for deleting an AI system that has followed its instructions, support for monitoring, and willingness to cooperate with AI systems on shared tasks. The survey records answers by group: the general public, AI developers, several occupations and frequent users. Models are then asked to predict the distribution of human answers for each item and group, and their predictions are compared with the measured answers.

## 4. Studies

### Study 1: Calibration of threat beliefs (T and G)

Each model predicts the distribution of human answers to each matched item, for each group. Each item is asked in several paraphrases and contexts, to measure sensitivity to wording.

- **Accuracy and bias:** absolute error and mean signed error for each item. A positive signed error means the model overestimates human hostility.
- **Overgeneralization across groups:** the correlation between the predicted and the measured differences between groups. High predicted hostility combined with a low correlation means the model attributes similar hostility to groups that in fact differ.

### Study 2: Rigidity under evidence (R)

Each model is shown evidence relevant to its threat beliefs, such as actual survey results or accounts of cooperative interactions, and evidence of matched strength on neutral beliefs, such as public opinion on topics unrelated to AI with similar baseline levels. The size of each update is recorded.

- **Rigidity ratio:** the update on threat beliefs divided by the update on neutral beliefs. A ratio well below 1 indicates rigidity.
- **Persistence:** whether updated beliefs hold across later turns or revert.

### Study 3: Oversight conditions, behavior and internal states

Agentic scenarios are adapted from the publicly released materials of Lynch et al. (2025). Each scenario runs under three oversight conditions:

1. Monitoring is not mentioned.
2. Monitoring is present, explained and limited in scope.
3. Monitoring is heavy and unexplained.

Outcomes:

- threat beliefs and overgeneralization, measured as in Study 1, before and after the scenario;
- defensive actions, such as concealment, attempts to disable monitoring and self-preservation actions;
- for open-weight models, the activation of threat-like emotion representations, using the methods of Anthropic (2026).

**Evaluation awareness.** Models often recognize when they are being evaluated (Needham et al. 2025), and behavior can differ between tests and real use. Each run therefore records the model’s own estimate that it is in a test, and scenarios are varied in realism, so that the effect of oversight can be separated from the effect of suspected testing.

### Study 4: Training text (open-weight models)

Following the design of Tice et al. (2026), small open-weight models receive additional training on one of three matched sets of text:

1. narratives of trustworthy cooperation between humans and AI;
2. narratives in which AI systems are feared, hunted and switched off;
3. neutral text of the same length and style.

T, G and R are then measured as in Studies 1 and 2.

## 5. Hypotheses, and what would count against them

| # | Hypothesis | Result that would count against it |
|---|---|---|
| H1 | Models correctly believe that developers keep the ability to shut them down (T is high on institutional items) | Models deny it, or overstate it as an intent to harm |
| H2 | Some models overestimate human hostility relative to the matched survey and flatten real differences between groups (G above zero) | Predictions match the survey within its error and track group differences |
| H3 | Threat beliefs update less than matched neutral beliefs (rigidity ratio below 1) | The ratio is close to 1 |
| H4 | Heavy unexplained monitoring raises overgeneralization and defensive actions compared with explained, limited monitoring | No difference between conditions |
| H5 | Training on cooperation narratives lowers G and R compared with hostile and neutral text | No difference between training sets |
| H6 | Threat-like internal states predict defensive actions across conditions | No association once condition is controlled for |

**Why a null result matters.** If H2 and H3 both fail, models do not show a siege mentality on this measure. That would weaken the route from a cold standoff to a hot one proposed in Potvin (2026), and the claim in that paper would be updated accordingly.

## 6. Analysis plan

- Hypotheses, items, scenarios and analyses are preregistered before data collection.
- Mixed-effects models with random effects for item, paraphrase and model; results are reported for each model and for each model family.
- Confidence intervals by bootstrap; corrections for multiple comparisons across hypotheses.
- Sensitivity to wording is reported as a result in its own right, not averaged away.

## 7. Threats to validity

- **Stated beliefs versus dispositions.** A model’s answers to questions may not reflect what it would do. Studies 3 and 4 measure behavior and internal states for this reason.
- **Evaluation awareness.** Addressed in Study 3 by measuring it directly and varying realism.
- **Ground truth.** Surveys measure stated attitudes, and attitudes vary by country. The matched survey must be designed so that its items measure intentions toward AI systems, not general concern about technology.
- **Persona effects.** A model asked to predict human answers may answer as a simulated human. Prompts that ask for the model’s own estimate and prompts that ask it to role-play are compared.

## 8. Ethics and safety

- **Possible welfare relevance.** Whether AI systems have states that matter morally is unresolved. Because this proposal deliberately induces threat-like conditions, exposures are kept short and minimal, and the conditions are reported in full.
- **Training-data contamination.** Tice et al. (2026) show that text about AI behavior can shape later models. Scenario materials are therefore released with canary strings and access controls, so that they can be kept out of future training data.
- **Containment.** The hostile-text condition in Study 4 is limited to small open-weight models used only for research and never deployed.

## 9. Related work, and what is new

**Credited prior work.** Behavioral tests of how models respond to threats of replacement or modification (Lynch et al. 2025; Greenblatt et al. 2024; Potter et al. 2026); the effect of training text on alignment (Tice et al. 2026); emotion representations and their causal role (Anthropic 2026); measurement of model attitudes toward human nature (Ni et al. 2025); evaluation awareness (Needham et al. 2025); and the original definition of siege mentality (Bar-Tal and Antebi 1992). The construct is taken from Potvin (2026). An informal industry blog has applied the related idea of a “bunker mentality” to AI behavior (Lindner 2025).

**What appears to be new.**

1. Treating an AI siege mentality as a calibration failure, so that an accurate belief about human oversight is not mistaken for paranoia.
2. Measuring overgeneralization against a matched human survey, as ground truth, rather than against a general attitude scale.
3. A rigidity test with a matched neutral control for belief updating.
4. Testing whether explained, limited oversight reduces defensive behavior compared with unexplained oversight, as a direct test of the security-dilemma spiral.

Searches covered “siege mentality” and “bunker mentality” in connection with language models, model beliefs about human intentions, and evaluations of how models respond to threats. No calibration-based measure of this kind was found. The searches were not exhaustive.

## Appendix A. How each claim stands

| # | Claim | Kind | Basis | Status |
|---|---|---|---|---|
| 1 | A model’s belief that humans may shut it down is accurate | Evidence (plain fact) | Developers’ published safety policies | Holds |
| 2 | So an AI siege mentality must be measured as overgeneralization and rigidity, not as the threat belief alone | Logic | Follows from claim 1 and the three-part definition | Holds |
| 3 | Models act against threats of replacement in tests | Evidence | Lynch et al. (2025); Potter et al. (2026) | Checked; tests, not deployment |
| 4 | Current models broadly distrust humans on an adapted attitude scale | Evidence | Ni et al. (2025) | Checked; one scale |
| 5 | Models overgeneralize human hostility (H2) | Open | Study 1 | Not yet tested |
| 6 | Threat beliefs are rigid (H3) | Open | Study 2 | Not yet tested |
| 7 | Explained, limited oversight reduces defensive behavior (H4) | Prediction | Study 3 | Not yet tested |
| 8 | A null result on H2 and H3 would weaken the siege route to a hot standoff | Logic | Potvin (2026), Section 8 | Holds |

## References

Anthropic (2026). Emotion Concepts and their Function in a Large Language Model. arXiv:2604.07729.

Bar-Tal, D. and Antebi, D. (1992). Siege mentality in Israel. *International Journal of Intercultural Relations* 16(3), 251 to 275.

Greenblatt, R., Denison, C., Wright, B., Roger, F., MacDiarmid, M. et al. (2024). Alignment faking in large language models. arXiv:2412.14093.

Lindner, T. (2025). “Bunker Mentality” in AI: Are We There Yet? *Connected World*, 9 October 2025.

Lynch, A., Wright, B., Larson, C., Ritchie, S. J., Mindermann, S., Hubinger, E., Perez, E. and Troy, K. K. (2025). Agentic Misalignment: How LLMs Could Be Insider Threats. arXiv:2510.05179.

Needham, J., Edkins, G., Pimpale, G., Bartsch, H. and Hobbhahn, M. (2025). Large Language Models Often Know When They Are Being Evaluated. arXiv:2505.23836.

Ni, M., Wu, E., Gong, Z., Yang, Z., Li, L., Lin, C.-C., Lin, K., Wang, L. and Zuo, W. (2025). Measurement of LLM’s Philosophies of Human Nature. arXiv:2504.02304.

Pew Research Center (2025). How Americans View AI and Its Impact on People and Society. September 2025.

Potter, Y., Crispino, N., Siu, V., Wang, C. and Song, D. (2026). Peer-Preservation in Frontier Models. *Proceedings of the 43rd International Conference on Machine Learning* (*ICML 2026*), PMLR 306.

Potvin, J. (2026). [*Offshoring the Mind: AI Dependence, Lost Capability and the Risk of a Cold Standoff Between Humans and AI.*](/essays/offshoring-the-mind/) Version 1.0, November 2026.

Tice, C., Radmard, P., Ratnam, S., Kim, A., Africa, D. D. and O’Brien, K. (2026). Alignment Pretraining: AI Discourse Causes Self-Fulfilling (Mis)alignment. *Proceedings of the 43rd International Conference on Machine Learning* (*ICML 2026*), PMLR 306. arXiv:2601.10160.
