# FuzzForce

FuzzForce finds the test case your wrong-answer solution fails on.

Give it a competitive programming problem and a solution that gets "wrong answer". It returns the smallest input that breaks the solution, confirmed by actually running the code, along with a short explanation of the bug.

Built for the Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026). Indie Developer track, theme: Build for Your World. It runs on Muse Spark through the Meta Model API, with Muse Wonder for harder problems.

All code in this repository was written during the hackathon.

## The problem

Every competitive programmer has seen "wrong answer on test 7" without being able to see test 7. The usual fix is to write a brute-force solution and a random generator by hand, run both against your code for a while, and hope something differs. It works, but it takes time on every problem, and it is easy to get the brute force or the generator wrong and chase a bug that isn't there.

FuzzForce automates that whole loop and refuses to report anything it has not verified.

## How it works

1. **Read the statement.** The problem statement goes to Muse Spark, which returns structured JSON containing an input validator, a brute-force reference solution, a second reference written with a different approach, and generators for random, edge-case and adversarial inputs.
2. **Check the generated pieces.** The validator must accept the sample inputs, and both references must reproduce the sample outputs. If a check fails, the model sees the error and repairs its code. If it keeps failing, the problem is escalated to Muse Wonder.
3. **Hunt for a failing input.** Each generator produces inputs. An input is kept only if it passes the validator. The submission and both references run on it inside a sandbox with time and memory limits.
4. **Confirm.** A failure counts only when both references agree with each other and the submission disagrees with them.
5. **Shrink.** The failing input is reduced by removing lines, lowering sizes and simplifying values. A candidate is kept only if it still passes the validator and the submission still fails on it.
6. **Explain.** The model gets the statement, the submission, the minimal input, the expected output and the actual output, and writes a two to three sentence explanation of the bug.

### The reporting rule

A counterexample is reported only if the input passes the validator and two independently written references agree on the answer. If that cannot be established, FuzzForce says so instead of guessing.

## Evaluation

Evaluated on CodeContests problems that have known-wrong submissions. The known-correct solutions in the dataset act as the oracle, so any reported counterexample on which a correct solution disagrees with the references is counted as a false counterexample.

Compared against a single-shot baseline where the model is asked to guess a breaking input with no execution loop.

| Metric | FuzzForce | Single-shot baseline |
| --- | --- | --- |
| Problems evaluated | TBD | TBD |
| Real counterexample found | TBD | TBD |
| False counterexamples | TBD | TBD |
| Median input size before shrinking | TBD | TBD |
| Median input size after shrinking | TBD | n/a |
| Average cost per problem | TBD | TBD |

Ablations:

| Variant | Found rate | False rate |
| --- | --- | --- |
| Full pipeline | TBD | TBD |
| No validator | TBD | TBD |
| One reference instead of two | TBD | TBD |
| No shrinking | TBD | TBD |
| Muse Spark only, no Wonder escalation | TBD | TBD |

Results, the raw run logs and the failure analysis are in `results/`.

## Setup

Requirements: Python 3.11 or newer, a Meta Model API key, and a C++ compiler if you want to test C++ submissions.

```
git clone https://github.com/<your-username>/fuzzforce.git
cd fuzzforce
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the key at the Meta Model API dashboard and export it:

```
export MODEL_API_KEY="your-key"
```

The key is read from the environment and is never stored in the repository.

To download the evaluation data:

```
python scripts/download_data.py
```

The dataset is not included in this repository.

## Usage

```
python -m fuzzforce run \
  --statement problem.txt \
  --solution wrong.py
```

Output:

- the minimal failing input
- the expected output and the output of the submission
- a short explanation of the bug

To run the evaluation:

```
python -m fuzzforce eval --limit 100
```

## Project structure

```
fuzzforce/
  sandbox.py      runs code with time and memory limits
  model.py        Meta Model API client, structured output, token logging
  generate.py     builds the validator, references and generators
  check.py        trust checks on the generated pieces
  search.py       runs generators and finds failing inputs
  shrink.py       reduces a failing input
  explain.py      writes the bug explanation
  eval/           evaluation harness and baseline
scripts/
  download_data.py
results/
```

## Scope and limitations

- Problems must have a single correct output for each input. Problems with multiple valid answers, interactive problems and problems with floating-point answers are not supported yet.
- Supported languages for submissions: Python and C++.
- Failures reported are wrong answers and runtime errors. Time limit failures are not reported in this version.
- The two references are written by the same model family, so they can share a mistake. Prompting them toward different approaches reduces this, and the disagreement rate is logged, but it does not remove the risk.
- Very large problems where even a correct brute force cannot finish on small inputs cannot be checked.

## Built with

- Meta Model API: Muse Spark for generation, repair and explanations, Muse Wonder for escalation. Uses structured output and tool calling.
- Python and the OpenAI-compatible SDK
- CodeContests, released by DeepMind, for evaluation. See the dataset's license for terms of use.

## Built during the hackathon

Everything in this repository, including the sandbox, the model client, the generation and checking pipeline, the shrinker and the evaluation harness, was written between Oct 26 and Nov 4, 2026. The commit history shows the order of work. External pieces are the Meta Model API, the CodeContests dataset and the open source libraries listed in `requirements.txt`.

## License

MIT
