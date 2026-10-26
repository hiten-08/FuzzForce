# FuzzForce

When a Codeforces submission gets "wrong answer on test 7", you can't see test 7. So you do what everyone does: write a brute force, write a random generator, run both against your code and hope something differs. I've done this more times than I'd like to admit.

FuzzForce does it for you. Give it the problem statement and your wrong solution, and it gives back the smallest input that breaks your code, plus a couple of sentences on what went wrong. Every counterexample is checked by actually running the code before it's shown to you.

I'm building this for the Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026), in the indie track under "Build for Your World". It uses Muse Spark and Muse Wonder through the Meta Model API. Everything in this repo was written during the hackathon.

## How it works

The problem statement goes to Muse Spark, which writes four things: a validator for the input format, a brute-force solution, a second solution that uses a different approach, and a few generators (random, edge cases, adversarial).

None of that is trusted yet. FuzzForce first runs it on the sample inputs. If the validator rejects a sample, or either solution gets a sample wrong, the model is shown the error and tries again. If it still can't get it right, the problem goes to Muse Wonder.

Once the pieces pass, the generators produce inputs, the validator throws out the invalid ones, and your solution and both references run on the rest inside a sandbox with time and memory limits. An input only counts as a failure when the two references agree with each other and your solution doesn't. That rule is the point of the whole project: if FuzzForce can't confirm a failure, it says so instead of guessing.

The failing input then gets shrunk. It removes lines, lowers n, simplifies values, and keeps a change only if the input is still valid and your solution still fails on it. When nothing more can be removed, the model gets the statement, your code, the small input and both outputs, and writes the explanation.

## Results

I'm testing on CodeContests problems that have known-wrong submissions, and comparing against a baseline where the model just guesses a breaking input without running anything. The known-correct solutions in the dataset let me catch false counterexamples.

The numbers will go here once the full run is done.

## Running it

You need Python 3.11 or newer and a Meta Model API key. A C++ compiler is only needed if you want to test C++ submissions.

```
git clone https://github.com/hiten-08/fuzzforce.git
cd fuzzforce
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MODEL_API_KEY="your-key"
```

To check a solution:

```
python -m fuzzforce run --statement problem.txt --solution wrong.py
```

To run the evaluation (downloads the dataset first):

```
python scripts/download_data.py
python -m fuzzforce eval --limit 100
```

## What's in the repo

```
fuzzforce/
  sandbox.py     runs code with time and memory limits
  model.py       talks to the Meta Model API and logs token use
  generate.py    asks the model for the validator, references and generators
  check.py       tests the generated pieces on the samples
  search.py      runs the generators and looks for a failing input
  shrink.py      makes a failing input smaller
  explain.py     writes the bug explanation
  eval/          evaluation and the baseline
scripts/
  download_data.py
results/
```

## Limits

- Only problems with one correct output per input. No interactive problems, no "print any valid answer", no floating-point answers.
- Python and C++ submissions only.
- It reports wrong answers and runtime errors, not time limit failures.
- Both references come from the same model family, so they can share a mistake. Asking for different approaches helps, but it doesn't remove the risk.
- If even a correct brute force can't finish on small inputs, FuzzForce can't check the problem.

## Credits

The evaluation uses CodeContests from DeepMind. Check the dataset's own license before reusing it. Models come from Meta's Muse family through the Meta Model API.

MIT license.
