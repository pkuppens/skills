# Test-driven development: the Bowling Game Kata

A workshop of about 1 hour. You need basic Python. You know the term TDD and
the words "red, green, refactor", but you have not seen it done step by step.
Start here.

## The idea in one sentence

**Write a test that fails, write the smallest code that makes it pass, then
clean up the code while all tests stay green.**

## What you do

You write a program that calculates the score of a bowling game. Bowling is a
good example: the rules are short, but a bonus depends on rolls that did not
happen yet. Halfway through, that rule forces a design change. The tests make
that change safe.

| Station | The test | What you learn |
| --- | --- | --- |
| 0 | `assert True == False` | Prove that the test runner can fail before you trust a pass. |
| 1 | A gutter game scores 0 | A test that cannot run is also red. Fake the first answer. |
| 2 | All ones score 20 | Test code must also be clean: a fixture and a helper. |
| 3 | One spare | The design is wrong. Skip the test, refactor on green, then bring it back. |
| 4 | One strike | Give each rule a name, so the code reads like the rules. |
| 5 | A perfect game scores 300 | A test that passes at once is suspect. Break the code on purpose to see it fail. |

## Open it

The notebook is [notebooks/bowling_kata.ipynb](notebooks/bowling_kata.ipynb).
GitHub shows it with all results stored. You do not need to install anything
to read it.

To run it yourself, you need Python 3.12 and [uv](https://docs.astral.sh/uv/):

```bash
cd workshops/test-driven-development
uv sync
uv run jupyter nbconvert --to notebook --execute notebooks/bowling_kata.ipynb --output my_bowling_kata.ipynb
```

To work cell by cell, run `uv sync --group lab`, then `uv run jupyter lab`. Or
open the notebook in VS Code and select the `.venv` kernel. Files named
`my_*.ipynb` are not tracked by Git.

## How the notebook is made

The tests run with [pytest](https://docs.pytest.org/) inside the notebook,
through [ipytest](https://github.com/chmp/ipytest). We do not write our own
test framework.

The script [notebooks/build_bowling_kata.py](notebooks/build_bowling_kata.py)
writes the cells, and a real run writes the results. The script never writes
a result. This workshop uses the notebook rules of the legacy-refactor
workshop: [../legacy-refactor/notebooks/README.md](../legacy-refactor/notebooks/README.md).

```bash
# from the repo root
uv run --project workshops/test-driven-development python workshops/test-driven-development/notebooks/build_bowling_kata.py
uv run --project workshops/test-driven-development jupyter nbconvert --to notebook --execute --inplace workshops/test-driven-development/notebooks/bowling_kata.ipynb
```

## Related

- The [legacy-refactor workshop](../legacy-refactor/README.md) uses tests as
  the checker for changes that alter behaviour. This kata shows the method on
  a small, clean problem first.

## Licence

[CC BY-NC-ND 4.0](../LICENSE), like all of `workshops/`.
