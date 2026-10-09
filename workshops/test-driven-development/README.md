# Test-driven development: the Bowling Game Kata

You need basic Python. You know the term TDD and the words "red, green,
refactor", but you have not seen it done step by step. Start here.

There are two notebooks with the same tests:

- **Read it, about 15 minutes:** [notebooks/bowling_kata.ipynb](notebooks/bowling_kata.ipynb)
  has every result stored. GitHub shows it, so you do not need to install
  anything.
- **Do it, about 1 hour:** [notebooks/bowling_kata_exercise.ipynb](notebooks/bowling_kata_exercise.ipynb)
  gives the tests, and you write the code. This is the workshop.

## The idea in one sentence

**Write a test that fails, write the smallest code that makes it pass, then
clean up the code while all tests stay green.**

## What you do

You write a program that calculates the score of a bowling game. Bowling is a
good example: the rules are short, but a bonus depends on rolls that did not
happen yet. Halfway through, that rule forces a design change. The tests make
that change safe. At the end, you change the finished program the way you
change code that somebody else wrote.

| Station | The test | What you learn |
| --- | --- | --- |
| 0 | `assert True == False` | Prove that the test runner can fail before you trust a pass. |
| 1 | A game without pins scores 0 | A test that cannot run is also red. Fake the first answer. |
| 2 | The score is the sum of the pins | Test code must also be clean: a fixture and a helper with named arguments. |
| 3 | The spare bonus is the next roll | The design is wrong. Skip the test, refactor on green, then bring it back. |
| 4 | The strike bonus is the next two rolls | Give each rule a name, so the code reads like the rules. |
| 5 | The strike bonus uses rolls, not frames | A test that passes at once is suspect. Break the code so that only this test can see it. |
| 6 | An unfinished game has no score | Change existing code: ask it what it does, pin that, make one place to change, then change it test-first. |

The exercises at the end continue from station 6: two tests that pass at once
and need a negative control, and one red test to make green.

## Credit

The Bowling Game Kata is by Robert C. Martin
([butunclebob.com](http://butunclebob.com/ArticleS.UncleBob.TheBowlingGameKata)),
and so are the three rules of TDD in the notebook (his "Three Laws of TDD",
*Clean Code*, chapter 9). Stations 1 to 5 follow his order of tests. The
negative controls, station 6 and the exercises are added for this workshop.
Station 6 uses the characterization test from Michael Feathers, *Working
Effectively with Legacy Code*.

## Run it

You need Python 3.12 and [uv](https://docs.astral.sh/uv/).

To do the exercise, copy the notebook first, so that your work is not
overwritten by `git pull`:

```bash
cd workshops/test-driven-development
uv sync --group lab
cp notebooks/bowling_kata_exercise.ipynb notebooks/my_bowling_kata.ipynb
uv run jupyter lab notebooks/my_bowling_kata.ipynb
```

Or open your copy in VS Code and select the `.venv` kernel. Files named
`my_*.ipynb` are not tracked by Git.

To run the reference notebook again:

```bash
cd workshops/test-driven-development
uv sync
uv run jupyter nbconvert --to notebook --execute notebooks/bowling_kata.ipynb --output my_bowling_kata_run.ipynb
```

## How the notebooks are made

The tests run with [pytest](https://docs.pytest.org/) inside the notebook,
through [ipytest](https://github.com/chmp/ipytest). We do not write our own
test framework.

The script [notebooks/build_bowling_kata.py](notebooks/build_bowling_kata.py)
writes the cells of both notebooks from one list. In the exercise notebook,
each answer cell becomes an empty "your turn" cell. A real run writes the
results of the reference notebook. The script never writes a result. This
workshop uses the notebook rules of the legacy-refactor workshop:
[../legacy-refactor/notebooks/README.md](../legacy-refactor/notebooks/README.md).

```bash
# from the repo root
uv run --project workshops/test-driven-development python workshops/test-driven-development/notebooks/build_bowling_kata.py
uv run --project workshops/test-driven-development jupyter nbconvert --to notebook --execute --inplace workshops/test-driven-development/notebooks/bowling_kata.ipynb
```

The exercise notebook is committed without results, because the learner
writes them.

## Related

- The [legacy-refactor workshop](../legacy-refactor/README.md) changes the
  behaviour of existing C# and C++ code in `02_test_driven_development`.
  Station 6 of this kata is the same method on a small Python class: ask the
  code what it does, pin that behaviour, then change it test-first.

## Licence

[CC BY-NC-ND 4.0](../LICENSE), like all of `workshops/`.
