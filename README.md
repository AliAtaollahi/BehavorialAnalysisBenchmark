# BehavorialAnalysisBenchmark

Timed Rebeca behavioral-equivalence benchmark for evaluating whether LLMs can
recognize revisions that preserve observable behavior. This repository publishes
the **40 selected comparison scenarios** in the supplied experiment artifact.

## Contents

- `cases/`: 40 scenarios, eight for each of five subject models.
- `answers.csv`: supplied expected verdicts, recorded Gemini/ChatGPT/Qwen answers,
  and the original shared-conversation links. A blank answer is missing data.
- `validate.py`: dependency-free integrity check and recorded-result summary.

Each scenario directory contains:

```text
program_1.rebeca          first Timed Rebeca program
program_2.rebeca          second Timed Rebeca program
observable_messages.txt  instance-qualified observable message names and time
prompt.txt               complete prompt used for the comparison
```

The programs, observable files, prompts, and answer table are preserved from the
supplied `cases` artifact. Differences in prompt indentation are intentional.
The selected pairs contain 45 distinct revisions; the full set of 150 revisions
discussed in the paper is not included here.

## Scenarios

| Subject model | Cases | Observable messages (excluding time) |
|---|---:|---:|
| Smart-home heater | 8 | 3 |
| Water treatment testbed | 8 | 6 |
| Two-actor example M_AB | 8 | 1 |
| Sensor network | 8 | 4 |
| Secure water treatment (SWaT) | 8 | 5 |

| CSV category | Pair type | Cases | Expected verdict |
|---|---|---:|---|
| `true-positive` | TP–TP | 20 | `YES` |
| `true-negative` | TP–TN | 10 | `NO` |
| `false-negative` | TP–FN | 10 | `YES` |

TP/TN/FN refer to the conservative **syntactic check**, not the LLM answer.
An FN revision is behaviorally equivalent even though the syntactic check cannot
establish it. There are 30 equivalent pairs and 10 non-equivalent pairs.

## Semantics

The complete semantics and weak timed bisimulation definition appear in each
`prompt.txt`. In this benchmark fragment, handlers are atomic and take zero time;
messages are asynchronous and stored in unordered bags; `after` controls arrival
time; and eligible message choices are nondeterministic. Unselected handler
executions are internal (`tau`). Time remains observable and accumulates across
internal transitions. Internal `delay` statements and `deadline` annotations are
outside the prompt's fragment.

Observation selects **handler execution**, not message sending. Selectors such as
`controller.getsense` name a rebec instance and message server. The timed
comparison retains time and ignores hidden internal actions.

## Validate the artifact

Requires Python 3.10 or newer, with no external packages:

```bash
python validate.py
```

The check verifies the case/answer correspondence, required files, category
labels, repeated revision contents, prompt/program consistency, and recorded
answer values. It also summarizes recorded answers, counting missing answers
separately. It **does not recompute semantic ground truth**.

For formal checking, generate `.statespace` files with Afra for the two programs
and pass them to [SemanticChecker](https://github.com/AliAtaollahi/SemanticChecker)
with the scenario's `observable_messages.txt`:

```bash
python /path/to/SemanticChecker/semantic_checker.py \
    program_1.statespace program_2.statespace observable_messages.txt \
    --equivalence weak-bisim
```

The benchmark contains Rebeca source programs, not pre-generated state spaces.
Expected answers are the supplied reference labels; validating the artifact
alone does not independently certify them.

## License

MIT; see [LICENSE](LICENSE).
