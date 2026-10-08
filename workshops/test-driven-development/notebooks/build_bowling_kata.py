"""Author bowling_kata.ipynb. Run from the repo root, then execute the notebook.

This script only writes the cells. It never writes outputs: the outputs come
from a real kernel run via `jupyter nbconvert --execute`. See
../../legacy-refactor/notebooks/README.md, rule 2.
"""
import os

import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))

nb = nbf.v4.new_notebook()
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda t: nbf.v4.new_code_cell(t)

nb.cells = [
md("""\
# Test-driven development — the Bowling Game Kata

## In short

**The goal.** You write a program that calculates the score of a bowling game.
You write each test **before** the code that makes it pass.

**Why this example.** The rules of bowling are short, but one rule looks into
the future: a bonus comes from rolls that did not happen yet. That rule forces
a design change in the middle of the work. You see how the tests make that
change safe.

**How.** In small cycles. Each cycle has three steps:

| Step | What you do | What you see |
| --- | --- | --- |
| 🔴 **Red** | Write one new test. Run it. | The test fails. |
| 🟢 **Green** | Write the smallest code that makes the test pass. | All tests pass. |
| 🔵 **Refactor** | Make the code clean. Do not change what it does. | All tests still pass. |

**The result.** Five tests and one small `Game` class. Each line of the class
exists because a test asked for it.

### The rules of bowling

- A game has **10 frames**.
- In each frame, the player has **2 rolls** to knock down **10 pins**.
- The score of a frame is the number of pins knocked down, plus a bonus:
  - **Spare:** all 10 pins fall in 2 rolls. The bonus is the pins of the
    **next 1 roll**.
  - **Strike:** all 10 pins fall in the first roll. The frame ends. The bonus
    is the pins of the **next 2 rolls**.
- In the 10th frame, a spare gives 1 extra roll and a strike gives 2 extra
  rolls. These rolls only give the bonus. They are not a new frame.

### TDD in three rules

1. Do not write program code until you have a test that fails.
2. Write only enough of a test to make it fail. Code that does not run is also
   a failure.
3. Write only enough program code to make the failing test pass.

**Why red first?** A test that you never saw fail proves nothing. It can pass
because it checks the wrong thing. The red step proves that the test can see a
problem.

### Three things to remember

1. **Red first.** Each test must fail one time before it passes.
2. **Small steps.** One test, then the smallest change. Do not write code that
   no test asks for.
3. **Refactor only on green.** When all tests pass, you can change the
   structure safely. The tests tell you at once if you broke something.

### The stations

0. Set up the test runner, and prove it can fail.
1. A gutter game: every roll hits 0 pins.
2. All ones: every roll hits 1 pin.
3. One spare: the design must change.
4. One strike.
5. A perfect game, and a check that this test can fail.
"""),

md("""\
## How to run it

You can read this notebook on GitHub. The results are stored in it. To run it
yourself:

```bash
cd workshops/test-driven-development
uv sync                                   # one time: Python and packages
uv run jupyter nbconvert --to notebook --execute notebooks/bowling_kata.ipynb --output my_bowling_kata.ipynb
```

To work in it cell by cell, use `uv sync --group lab`, then
`uv run jupyter lab`. Or open it in VS Code and select the `.venv` kernel.

### Pitfalls

| Problem | Cause | What to do |
| --- | --- | --- |
| `ModuleNotFoundError: ipytest` | The wrong kernel is selected. | Select the Python in `workshops/test-driven-development/.venv`. |
| A red result where this page shows green, or the other way | The cells ran out of order. Each cell changes the code or the tests. | Restart the kernel and run all cells from the top. |
| A changed cell has no effect | You edited the cell but did not run it. | Run the cell. The test run is part of the same cell. |

### About this notebook

| | |
| --- | --- |
| **Method** | Test-driven development (red, green, refactor) |
| **Needs** | Python 3.12 and `uv`. No network after `uv sync`. |
| **Run time** | less than 10 seconds |
| **State** | EXECUTED |
| **Used by** | `02_test_driven_development` in [../../legacy-refactor/](../../legacy-refactor/README.md) |
"""),

md("""\
## 0 — Set up the test runner

A **test** is a small function that runs some code and checks the result. The
check is an **assert**: `assert x == y` passes when `x` equals `y`, and fails
when it does not.

We use **pytest**, the most common test tool for Python. The package
**ipytest** runs pytest inside a notebook. A cell that starts with `%%ipytest`
first runs its code, then runs **all** the tests that exist in the notebook.

We do not write our own test framework. pytest does the work, and it is the
same tool that you use in a real project.
"""),

code("""\
import ipytest
import pytest

ipytest.autoconfig(
    clean=False,            # keep the tests of earlier cells, so that each run tests everything
    addopts=[
        "-q",               # short report
        "--tb=no",          # no long error details ...
        "-rf",              # ... but one line with the reason for each failed test
        "-p", "no:cacheprovider",  # do not write a .pytest_cache folder
    ],
)
print("pytest", pytest.__version__)
"""),

md("""\
### 🔴 Red: prove that the runner can fail

Before we trust a green result, we must see a red result. This test is wrong
on purpose: `True` is never equal to `False`.
"""),

code("""\
%%ipytest

def test_environment():
    assert True == False
"""),

md("""\
pytest found the test, ran it, and reported `1 failed`. The line `FAILED ...`
gives the reason: `assert True == False`. So the runner works, and it can see
a problem.

### 🟢 Green: prove that the runner can pass
"""),

code("""\
%%ipytest

def test_environment():
    assert True == True
"""),

md("""\
`1 passed`. The test runner works in both directions.

This test only checked the runner. It does not test our program, so we delete
it now.
"""),

code("""\
del test_environment
"""),

md("""\
## 1 — A gutter game

**What we want next.** A player rolls 20 times and hits no pin each time (a
"gutter game"). The score is 0.

This is the simplest game. It forces us to decide the interface: a `Game` has
`roll(pins)` for each roll, and `score()` at the end.

### 🔴 Red
"""),

code("""\
%%ipytest

def test_gutter_game():
    game = Game()
    for _ in range(20):
        game.roll(0)
    assert game.score() == 0
"""),

md("""\
The test fails with `NameError: name 'Game' is not defined`. The class does
not exist yet. **Code that cannot run is also red.** We do not write the class
before we have this red result.

### 🟢 Green

We write the smallest code that passes. `score()` returns `0`, always. This
looks too simple, and it is correct on purpose: no test asks for more yet.
"""),

code("""\
%%ipytest

class Game:
    def roll(self, pins):
        pass

    def score(self):
        return 0
"""),

md("""\
`1 passed`.

### 🔵 Refactor

There is nothing to clean up yet. We continue.

## 2 — All ones

**What we want next.** The player hits 1 pin with each of the 20 rolls. The
score is 20. This test makes the "always 0" answer wrong.

### 🔴 Red
"""),

code("""\
%%ipytest

def test_all_ones():
    game = Game()
    for _ in range(20):
        game.roll(1)
    assert game.score() == 20
"""),

md("""\
`assert 0 == 20`. The program returns 0, the test expects 20. The old test
still passes.

### 🟢 Green

Add the pins of each roll to a total.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._score = 0

    def roll(self, pins):
        self._score += pins

    def score(self):
        return self._score
"""),

md("""\
`2 passed`.

### 🔵 Refactor: the tests

Test code must also be clean. Both tests make a `Game` and roll the same
number many times. We move these two things to one place:

- a **fixture** `game`: pytest makes a new `Game` for each test that asks for
  `game`;
- a helper `roll_many(game, n, pins)`.

We change only the structure of the tests. They must still pass.
"""),

code("""\
%%ipytest

@pytest.fixture
def game():
    return Game()

def roll_many(game, n, pins):
    for _ in range(n):
        game.roll(pins)

def test_gutter_game(game):
    roll_many(game, 20, 0)
    assert game.score() == 0

def test_all_ones(game):
    roll_many(game, 20, 1)
    assert game.score() == 20
"""),

md("""\
`2 passed`. Same tests, less repeated code.

## 3 — One spare

**What we want next.** The first frame is a spare: 5, then 5. The next roll
is 3. All other rolls hit 0 pins.

- Frame 1: 5 + 5 = 10, plus the bonus of the next roll (3) = **13**.
- Frame 2: 3 + 0 = **3**.
- Total: **16**.

### 🔴 Red
"""),

code("""\
%%ipytest

def test_one_spare(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, 17, 0)
    assert game.score() == 16
"""),

md("""\
`assert 13 == 16`. The program adds the pins and forgets the bonus.

### Stop: the design is wrong

Try to make this pass inside `roll()`. You cannot do it cleanly. When `roll()`
gets the 3, it does not know that the two rolls before it were a spare. It
does not know where a frame starts. **The design does not fit the rules.**

Do not hack a fix on a red test. Take one step back:

1. Skip the new test, so that all tests are green again.
2. Refactor the design while the old tests protect us.
3. Bring the new test back.

`@pytest.mark.skip` tells pytest not to run a test, and to report it as
skipped.
"""),

code("""\
%%ipytest

@pytest.mark.skip(reason="wait for the refactor: Game must know the frames")
def test_one_spare(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, 17, 0)
    assert game.score() == 16
"""),

md("""\
`2 passed, 1 skipped`. Green again.

### 🔵 Refactor: keep the rolls, count by frame

New design: `roll()` only keeps the pins in a list. `score()` walks through the
**10 frames**, 2 rolls at a time. The behaviour does not change, so the two old
tests must still pass.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        i = 0                      # index of the first roll of the frame
        for frame in range(10):
            total += self._rolls[i] + self._rolls[i + 1]
            i += 2
        return total
"""),

md("""\
`2 passed, 1 skipped`. The new design works for the old tests.

### 🔴 Red again

Remove the skip. The spare test must fail again, for the same reason as before.
"""),

code("""\
%%ipytest

def test_one_spare(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, 17, 0)
    assert game.score() == 16
"""),

md("""\
`assert 13 == 16`. Same failure. Now the design lets us fix it in one place.

### 🟢 Green

In a frame with a spare, add the next roll as a bonus.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        i = 0
        for frame in range(10):
            if self._rolls[i] + self._rolls[i + 1] == 10:   # spare
                total += 10 + self._rolls[i + 2]
            else:
                total += self._rolls[i] + self._rolls[i + 1]
            i += 2
        return total
"""),

md("""\
`3 passed`.

### 🔵 Refactor

Two things are not clear:

- In the program, the comment `# spare` explains the condition. A name is
  better than a comment: `_is_spare(i)`.
- In the test, `roll(5); roll(5)` needs the comment `# spare`. A helper
  `roll_spare(game)` says it in the code.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        frame_index = 0
        for frame in range(10):
            if self._is_spare(frame_index):
                total += 10 + self._rolls[frame_index + 2]
            else:
                total += self._rolls[frame_index] + self._rolls[frame_index + 1]
            frame_index += 2
        return total

    def _is_spare(self, frame_index):
        return self._rolls[frame_index] + self._rolls[frame_index + 1] == 10


def roll_spare(game):
    game.roll(5)
    game.roll(5)

def test_one_spare(game):
    roll_spare(game)
    game.roll(3)
    roll_many(game, 17, 0)
    assert game.score() == 16
"""),

md("""\
`3 passed`. The code now says "spare" where it means spare.

## 4 — One strike

**What we want next.** The first frame is a strike: 10 pins. The next two
rolls are 3 and 4. All other rolls hit 0 pins.

- Frame 1: 10, plus the bonus of the next two rolls (3 + 4) = **17**.
- Frame 2: 3 + 4 = **7**.
- Total: **24**.

A strike uses only **1 roll** for the frame. So this game has 19 rolls, not 20.

### 🔴 Red
"""),

code("""\
%%ipytest

def roll_strike(game):
    game.roll(10)

def test_one_strike(game):
    roll_strike(game)
    game.roll(3)
    game.roll(4)
    roll_many(game, 16, 0)
    assert game.score() == 24
"""),

md("""\
This red is an `IndexError`, not a wrong number. The program still thinks
that each frame has 2 rolls. It counts the strike frame as "10 and 3", and it
looks for a 20th roll that does not exist.

### 🟢 Green

A strike frame scores 10 plus the next 2 rolls, and moves on by **1** roll.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        frame_index = 0
        for frame in range(10):
            if self._rolls[frame_index] == 10:   # strike
                total += 10 + self._rolls[frame_index + 1] + self._rolls[frame_index + 2]
                frame_index += 1
            elif self._is_spare(frame_index):
                total += 10 + self._rolls[frame_index + 2]
                frame_index += 2
            else:
                total += self._rolls[frame_index] + self._rolls[frame_index + 1]
                frame_index += 2
        return total

    def _is_spare(self, frame_index):
        return self._rolls[frame_index] + self._rolls[frame_index + 1] == 10
"""),

md("""\
`4 passed`.

### 🔵 Refactor

Again a comment explains a condition. We give each idea a name. After this
step, `score()` reads like the rules at the top of this notebook.
"""),

code("""\
%%ipytest

class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        frame_index = 0
        for frame in range(10):
            if self._is_strike(frame_index):
                total += 10 + self._strike_bonus(frame_index)
                frame_index += 1
            elif self._is_spare(frame_index):
                total += 10 + self._spare_bonus(frame_index)
                frame_index += 2
            else:
                total += self._pins_in_frame(frame_index)
                frame_index += 2
        return total

    def _is_strike(self, frame_index):
        return self._rolls[frame_index] == 10

    def _is_spare(self, frame_index):
        return self._pins_in_frame(frame_index) == 10

    def _strike_bonus(self, frame_index):
        return self._rolls[frame_index + 1] + self._rolls[frame_index + 2]

    def _spare_bonus(self, frame_index):
        return self._rolls[frame_index + 2]

    def _pins_in_frame(self, frame_index):
        return self._rolls[frame_index] + self._rolls[frame_index + 1]
"""),

md("""\
`4 passed`. The refactor changed the structure, and the tests prove that the
behaviour stayed the same.

## 5 — A perfect game

**What we want next.** 12 strikes in a row: one for each of the 10 frames,
plus the 2 extra rolls of the 10th frame. Each frame scores 10 + 10 + 10 = 30.
The total is **300**.

### 🔴 Red?
"""),

code("""\
%%ipytest

def test_perfect_game(game):
    roll_many(game, 12, 10)
    assert game.score() == 300
"""),

md("""\
`5 passed`. **The new test passed at once.** There was no red step.

That can happen. The design from cycles 3 and 4 already handles it: the loop
stops after 10 frames, so the 2 extra rolls only count as bonus.

But rule 1 says: a test that you never saw fail proves nothing. So we make it
fail on purpose. This is a **negative control**: we break the program in a
known way, and we check that the test sees it.

### 🔴 Negative control: break the strike bonus

We replace `_strike_bonus` with a wrong version that forgets the second bonus
roll. We keep the correct version, so that we can put it back.
"""),

code("""\
%%ipytest

correct_strike_bonus = Game._strike_bonus
Game._strike_bonus = lambda self, frame_index: self._rolls[frame_index + 1]   # bug on purpose
"""),

md("""\
`2 failed`. The perfect-game test sees the bug, and so does the one-strike
test. Both tests can fail, so a green result from them means something.

### 🟢 Green: put the correct code back
"""),

code("""\
%%ipytest

Game._strike_bonus = correct_strike_bonus
del correct_strike_bonus
"""),

md("""\
`5 passed`. The kata is done.

## What we have

The list of tests is the specification of the program. Each name says one
rule of bowling:
"""),

code("""\
_ = ipytest.run("--collect-only")
"""),

md("""\
### What TDD gave us

- **The design came from the tests.** We did not plan a list of rolls or a
  frame loop at the start. The spare test showed that the first design was
  wrong, and the old tests made the change safe.
- **Each line has a reason.** No code exists that a test did not ask for.
- **A safety net.** We changed the `Game` class 6 times. After each change,
  all earlier tests ran again.
- **Proof that the tests work.** Each test failed one time. The perfect-game
  test did not, so we broke the program on purpose to see it fail.

### Next exercises (not in this notebook)

Do them with the same cycle: red, green, refactor. Some of them can pass at
once. Then make the test fail on purpose, as in station 5, before you trust it.

1. A spare in the 10th frame: 9 frames of 0 pins, then 5, 5, 3. The score is 13.
2. A real game from a score sheet, for example
   `10, 7, 3, 9, 0, 10, 0, 8, 8, 2, 0, 6, 10, 10, 10, 8, 1`. The score is 167.
3. Wrong input: a roll of 11 pins, or 2 rolls with more than 10 pins in one
   frame. Decide first what the program must do, then write the test.
"""),
]

nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = os.path.join(HERE, "bowling_kata.ipynb")
nbf.write(nb, out)
print("wrote", out, len(nb.cells), "cells")
