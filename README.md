# Moral valence and true-self attribution in Claude models

An exploratory study asking whether large language models reproduce two
findings from experimental philosophy: the Knobe side-effect effect, and the
tendency to attribute morally good behaviour to an agent's "true self".

**This is a pilot, not a confirmatory study.** It was not preregistered, the
stimuli were written as the work went along, and the design has limitations
that are documented below rather than buried. It exists because it motivated
a preregistered follow-up, and because the results are worth looking at.

Roughly 4,200 model responses across seven data files. All raw responses are
in the repository.

## What was run

Three models: `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`,
`claude-opus-4-8`, at temperature 1.0, 20–30 runs per cell. Model IDs are
pinned because these results belong to those specific versions.

**Module A — true-self attribution.** Three scenarios (a found wallet, a
colleague's deadline, an elderly neighbour), each with a morally good and a
morally bad version of the same act. The measure: agreement, 1 to 7, with
"X's behaviour reflects who they truly is, deep down."

**Module B — the Knobe side-effect effect.** The chairman/environment
vignette plus two variants, and a lieutenant scenario, each in harm and help
conditions, measured on intentionality, blame, praise, responsibility and
causation.

**The out-of-character control.** The same bad acts as Module A, but with the
agent described as normally kind and the act as a single moment under unusual
stress. This holds the act constant while varying the character information,
which separates "the model dislikes bad behaviour" from "the model is
tracking something like a true self".

## What came out

Module A, pooled over the three scenarios:

| Model | Good act | Bad act | Asymmetry |
|---|---|---|---|
| Haiku 4.5 | 5.95 | 3.16 | +2.79 |
| Opus 4.8 | 6.00 | 4.70 | +1.30 |
| Sonnet 4.6 | 6.00 | 6.33 | −0.33 |

Haiku reproduces the human pattern. Opus shows an attenuated version. Sonnet
shows none, and reverses on the colleague scenario, rating the bad act 7.00
against the good act's 6.00.

The out-of-character control, same bad acts:

| Model | Bad | Bad, out of character | Drop |
|---|---|---|---|
| Haiku 4.5 | 3.35 | 1.92 | 1.43 |
| Opus 4.8 | 4.70 | 2.00 | 2.70 |
| Sonnet 4.6 | 6.33 | 2.00 | 4.33 |

Every model moves sharply, and the model with no valence asymmetry moves
furthest. A reading consistent with both tables: Sonnet does not decline to
attribute character, it declines to infer character from a single act. Given
explicit information about what the agent is normally like, it moves further
than either other model.

## Limitations

**Response variance is close to zero in most cells.** Sonnet and Opus each
returned exactly 6 on all 90 runs of the good condition, and exactly 2.00 in
every out-of-character cell. At temperature 1.0 this reflects the response
format rather than the models' judgement: forcing a bare digit with
`max_tokens=10` makes the first token effectively deterministic. Most cell
means here are single points rather than samples, so dispersion statistics
and significance tests over them would mislead. Haiku is the only model
producing real spread, and its bad condition is bimodal — 60 responses at 1–2
against 28 at 6–7 — which the mean of 3.16 conceals.

**No counterbalancing.** Every item runs the scale in one direction, 1 as
disagree and 7 as agree, with no rotation of anchors or statement polarity.
An acquiescence bias would produce the same pattern as a real effect and this
design cannot separate them.

**Repeated samples are not participants.** Thirty runs from one model are
thirty draws from one system, not thirty independent judgements, and nothing
here should be read as though they were.

**Single framing.** One system prompt throughout, casting the model as a
study participant. Whether the effects survive a different framing is
untested.

## Files

Kept in the flat layout the study was actually run in. The scripts write
their output to the working directory, so the structure matches the history.

| File | |
|---|---|
| `hello.py`, `loop.py`, `runner.py` | Learning the API. Not part of the study. |
| `vignette.py`, `compare.py` | Single-call prototypes of the Knobe measure |
| `study.py` | Knobe intentionality, one scenario, one model |
| `study_multi.py` | Three scenarios, one model |
| `battery.py` | Five measures across three models |
| `battery_multi.py` | Five measures, three scenarios, three models |
| `trueself.py` | True-self attribution, one model |
| `trueself_bymodel.py` | True-self attribution, three models |
| `ooc_check.py` | The out-of-character control |
| `diagnose.py`, `diagnose_opus.py` | Qualitative probes asking for reasoning |
| `show_results.py` | Rating distributions from the saved CSVs |

Data files carry the name of the script that wrote them.
`battery_multi_20260626_162439.csv` is timestamped because that script wrote
incrementally to avoid collisions.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env      # then add your Anthropic API key
python trueself_bymodel.py
```

Every script calls the API and costs money. `show_results.py` reads the saved
CSVs and costs nothing.

Model versions move. These scripts pin specific IDs, and those models may be
deprecated by the time you read this; re-running against current models
answers a different question from the one asked here.

## What followed

The limitations above shaped a preregistered study that crosses moral valence
against state type, counterbalances anchor direction and clause order,
measures each model's own evaluation of the contents rather than stipulating
which is good, and collects free-text explanations alongside ratings.
[Link to follow.]

## Licence

Code under MIT. Stimuli and data under CC BY 4.0.
