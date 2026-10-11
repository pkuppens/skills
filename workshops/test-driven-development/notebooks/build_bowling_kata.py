"""Author bowling_kata.ipynb and bowling_kata_exercise.ipynb. Run from the repo root.

This script only writes the cells. It never writes outputs: the outputs come
from a real kernel run via `jupyter nbconvert --execute`. See
../../legacy-refactor/notebooks/README.md, rule 2.

Both notebooks come from one list of cells. In the exercise notebook, each cell
that holds an answer is replaced by an empty "your turn" cell, and the diff
that shows the answer is left out.
"""
import difflib
import os

import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
ANSWER = "answer"   # cell tag: left out of, or emptied in, the exercise notebook

YOUR_TURN = """\
%%ipytest

# Your turn: write the Game class here (start from a copy of your last
# version), then run this cell. One answer is in bowling_kata.ipynb.
"""


def md(text, *tags):
    return nbf.v4.new_markdown_cell(text, metadata={"tags": list(tags)} if tags else {})


def code(text, *tags):
    return nbf.v4.new_code_cell(text, metadata={"tags": list(tags)} if tags else {})


def ipytest_cell(source, *tags):
    return code("%%ipytest\n\n" + source, *tags)


def diff_of(old, new):
    """The change from one version of Game to the next, as a Markdown diff block."""
    lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=1))[2:]
    body = "\n".join("..." if line.startswith("@@") else line for line in lines)
    return f"The change:\n\n```diff\n{body}\n```"


def game_step(old, new):
    """Two cells: the diff from the last version, then the new version that the tests run."""
    cells = [] if old is None else [md(diff_of(old, new), ANSWER)]
    return cells + [ipytest_cell(new, ANSWER)]


# The versions of the Game class, in the order the notebook writes them.

GAME_FAKE = """\
class Game:
    def roll(self, pins):
        pass

    def score(self):
        return 0
"""

GAME_SUM = """\
class Game:
    def __init__(self):
        self._score = 0

    def roll(self, pins):
        self._score += pins

    def score(self):
        return self._score
"""

GAME_FRAMES = """\
FRAMES_PER_GAME = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            total += self._rolls[first_roll] + self._rolls[first_roll + 1]
            first_roll += 2
        return total
"""

GAME_SPARE = """\
FRAMES_PER_GAME = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._rolls[first_roll] + self._rolls[first_roll + 1] == 10:   # spare
                total += 10 + self._rolls[first_roll + 2]
            else:
                total += self._rolls[first_roll] + self._rolls[first_roll + 1]
            first_roll += 2
        return total
"""

GAME_SPARE_NAMED = """\
FRAMES_PER_GAME = 10
ALL_PINS = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._is_spare(first_roll):
                total += ALL_PINS + self._rolls[first_roll + 2]
            else:
                total += self._rolls[first_roll] + self._rolls[first_roll + 1]
            first_roll += 2
        return total

    def _is_spare(self, first_roll):
        return self._rolls[first_roll] + self._rolls[first_roll + 1] == ALL_PINS
"""

GAME_STRIKE = """\
FRAMES_PER_GAME = 10
ALL_PINS = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._rolls[first_roll] == ALL_PINS:   # strike
                total += ALL_PINS + self._rolls[first_roll + 1] + self._rolls[first_roll + 2]
                first_roll += 1
            elif self._is_spare(first_roll):
                total += ALL_PINS + self._rolls[first_roll + 2]
                first_roll += 2
            else:
                total += self._rolls[first_roll] + self._rolls[first_roll + 1]
                first_roll += 2
        return total

    def _is_spare(self, first_roll):
        return self._rolls[first_roll] + self._rolls[first_roll + 1] == ALL_PINS
"""

GAME_STRIKE_NAMED = """\
FRAMES_PER_GAME = 10
ALL_PINS = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._is_strike(first_roll):
                total += ALL_PINS + self._strike_bonus(first_roll)
                first_roll += 1
            elif self._is_spare(first_roll):
                total += ALL_PINS + self._spare_bonus(first_roll)
                first_roll += 2
            else:
                total += self._pins_in_frame(first_roll)
                first_roll += 2
        return total

    def _is_strike(self, first_roll):
        return self._rolls[first_roll] == ALL_PINS

    def _is_spare(self, first_roll):
        return self._pins_in_frame(first_roll) == ALL_PINS

    def _strike_bonus(self, first_roll):
        return self._rolls[first_roll + 1] + self._rolls[first_roll + 2]

    def _spare_bonus(self, first_roll):
        return self._rolls[first_roll + 2]

    def _pins_in_frame(self, first_roll):
        return self._rolls[first_roll] + self._rolls[first_roll + 1]
"""

GAME_ONE_READ = """\
FRAMES_PER_GAME = 10
ALL_PINS = 10


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._is_strike(first_roll):
                total += ALL_PINS + self._strike_bonus(first_roll)
                first_roll += 1
            elif self._is_spare(first_roll):
                total += ALL_PINS + self._spare_bonus(first_roll)
                first_roll += 2
            else:
                total += self._pins_in_frame(first_roll)
                first_roll += 2
        return total

    def _is_strike(self, first_roll):
        return self._pins(first_roll) == ALL_PINS

    def _is_spare(self, first_roll):
        return self._pins_in_frame(first_roll) == ALL_PINS

    def _strike_bonus(self, first_roll):
        return self._pins(first_roll + 1) + self._pins(first_roll + 2)

    def _spare_bonus(self, first_roll):
        return self._pins(first_roll + 2)

    def _pins_in_frame(self, first_roll):
        return self._pins(first_roll) + self._pins(first_roll + 1)

    def _pins(self, roll):
        return self._rolls[roll]
"""

GAME_FINISHED_CHECK = """\
FRAMES_PER_GAME = 10
ALL_PINS = 10


class IncompleteGameError(Exception):
    \"\"\"score() needs a roll that was not made yet.\"\"\"


class Game:
    def __init__(self):
        self._rolls = []

    def roll(self, pins):
        self._rolls.append(pins)

    def score(self):
        total = 0
        first_roll = 0
        for _ in range(FRAMES_PER_GAME):
            if self._is_strike(first_roll):
                total += ALL_PINS + self._strike_bonus(first_roll)
                first_roll += 1
            elif self._is_spare(first_roll):
                total += ALL_PINS + self._spare_bonus(first_roll)
                first_roll += 2
            else:
                total += self._pins_in_frame(first_roll)
                first_roll += 2
        return total

    def _is_strike(self, first_roll):
        return self._pins(first_roll) == ALL_PINS

    def _is_spare(self, first_roll):
        return self._pins_in_frame(first_roll) == ALL_PINS

    def _strike_bonus(self, first_roll):
        return self._pins(first_roll + 1) + self._pins(first_roll + 2)

    def _spare_bonus(self, first_roll):
        return self._pins(first_roll + 2)

    def _pins_in_frame(self, first_roll):
        return self._pins(first_roll) + self._pins(first_roll + 1)

    def _pins(self, roll):
        if roll >= len(self._rolls):
            raise IncompleteGameError(f"the game is not finished: roll {roll + 1} is missing")
        return self._rolls[roll]
"""


def header(exercise):
    if exercise:
        run_it = """\
This is the **exercise** version. The tests are given. You write the `Game`
class in each cell that says "Your turn". Copy the notebook first, so that
your work is not overwritten by `git pull`:

```bash
cd workshops/test-driven-development
uv sync --group lab                       # one time: Python and packages
cp notebooks/bowling_kata_exercise.ipynb notebooks/my_bowling_kata.ipynb
uv run jupyter lab notebooks/my_bowling_kata.ipynb
```

Or open your copy in VS Code and select the `.venv` kernel. One answer, with
every result stored, is in [bowling_kata.ipynb](bowling_kata.ipynb)."""
        state = "NOT EXECUTED. An exercise: you write the code."
        run_time = "about 1 hour"
    else:
        run_it = """\
You can read this notebook on GitHub. The results are stored in it. To run it
yourself:

```bash
cd workshops/test-driven-development
uv sync                                   # one time: Python and packages
uv run jupyter nbconvert --to notebook --execute notebooks/bowling_kata.ipynb --output my_bowling_kata.ipynb
```

To do the kata yourself, use
[bowling_kata_exercise.ipynb](bowling_kata_exercise.ipynb): the same tests,
without the answers."""
        state = "EXECUTED"
        run_time = "less than 10 seconds"

    return [
        md("""\
# Test-driven development — the Bowling Game Kata

## In short

**The goal.** You write a program that calculates the score of a bowling game.
You write each test **before** the code that makes it pass. Then you change
the finished program the way you change code that you did not write.

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

**The result.** Six tests and one small `Game` class. Each line of the class
comes from a failing test, or from a refactor that the tests protected.

**Credit.** The Bowling Game Kata and the three rules of TDD below are by
Robert C. Martin: the
[Bowling Game Kata](http://butunclebob.com/ArticleS.UncleBob.TheBowlingGameKata)
and the "Three Laws of TDD" (*Clean Code*, chapter 9). Stations 1 to 5 follow
his order of tests. The negative controls, station 6 and the exercises are
added for this workshop.

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

1. **Red first.** Each test must fail one time before you trust it.
2. **Small steps.** One test, then the smallest change. Do not write code that
   no test asks for.
3. **Refactor only on green.** When all tests pass, you can change the
   structure safely. The tests tell you at once if you broke something.

### The stations

0. Set up the test runner, and prove it can fail.
1. A game without pins.
2. Every roll hits 1 pin.
3. One spare: the design must change.
4. One strike.
5. A perfect game, and a check that this test can fail.
6. Change the finished program as if somebody else wrote it.
"""),
        md(f"""\
## How to run it

{run_it}

### Pitfalls

| Problem | Cause | What to do |
| --- | --- | --- |
| `ModuleNotFoundError: ipytest` | The wrong kernel is selected. | Select the Python in `workshops/test-driven-development/.venv`. |
| A red result where the text says green, or the other way | The cells ran out of order. Each cell changes the code or the tests. | Restart the kernel and run all cells from the top. |
| A changed cell has no effect | You edited the cell but did not run it. | Run the cell. The test run is part of the same cell. |
| `AttributeError: ... '_strike_bonus'` in station 5 | The negative control uses the method names from the hints in station 4. | Use those names, or change the negative control to your names. |

### About this notebook

| | |
| --- | --- |
| **Method** | Test-driven development (red, green, refactor), then a characterization test |
| **Needs** | Python 3.12 and `uv`. No network after `uv sync`. |
| **Run time** | {run_time} |
| **State** | {state} |
| **Used by** | `02_test_driven_development` in [../../legacy-refactor/](../../legacy-refactor/README.md) |
"""),
    ]


STATIONS = [
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

ipytest_cell("""\
def test_environment():
    assert True == False
"""),

md("""\
pytest found the test, ran it, and reported `1 failed`. The line `FAILED ...`
gives the reason: `assert True == False`. So the runner works, and it can see
a problem.

### 🟢 Green: prove that the runner can pass
"""),

ipytest_cell("""\
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
## 1 — A game without pins

**What we want next.** A player rolls 20 times and hits no pin each time (a
"gutter game"). The score is 0.

This is the simplest game. It forces us to decide the interface: a `Game` has
`roll(pins)` for each roll, and `score()` at the end.

Each test name says the rule that the test checks, not only the example. So
the list of names at the end reads like the rules of the game.

### 🔴 Red
"""),

ipytest_cell("""\
def test_a_game_without_pins_scores_zero():
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

*game_step(None, GAME_FAKE),

md("""\
`1 passed`.

### 🔵 Refactor

There is nothing to clean up yet. We continue.

## 2 — Every roll hits 1 pin

**What we want next.** The player hits 1 pin with each of the 20 rolls. The
score is 20. This test makes the "always 0" answer wrong.

### 🔴 Red
"""),

ipytest_cell("""\
def test_score_is_the_sum_of_the_pins():
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

*game_step(GAME_FAKE, GAME_SUM),

md("""\
`2 passed`.

### 🔵 Refactor: the tests

Test code must also be clean. Both tests make a `Game` and roll the same
number many times. We move these two things to one place:

- a **fixture** `game`: pytest makes a new `Game` for each test that asks for
  `game`;
- a helper `roll_many(game, rolls=..., pins=...)`. The `*` in its definition
  makes the names compulsory, so a call says which number is which.

We change only the structure of the tests. They must still pass.
"""),

ipytest_cell("""\
@pytest.fixture
def game():
    return Game()

def roll_many(game, *, rolls, pins):
    for _ in range(rolls):
        game.roll(pins)

def test_a_game_without_pins_scores_zero(game):
    roll_many(game, rolls=20, pins=0)
    assert game.score() == 0

def test_score_is_the_sum_of_the_pins(game):
    roll_many(game, rolls=20, pins=1)
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

ipytest_cell("""\
def test_spare_bonus_is_the_next_roll(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, rolls=17, pins=0)
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

ipytest_cell("""\
@pytest.mark.skip(reason="wait for the refactor: Game must know the frames")
def test_spare_bonus_is_the_next_roll(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, rolls=17, pins=0)
    assert game.score() == 16
"""),

md("""\
`2 passed, 1 skipped`. Green again.

### 🔵 Refactor: keep the rolls, count by frame

New design: `roll()` only keeps the pins in a list. `score()` walks through the
**10 frames**, 2 rolls at a time. `first_roll` is the place in the list where
the current frame starts. The behaviour does not change, so the two old tests
must still pass.

Be honest about where this design comes from: we did not discover it. It is
the known answer to this kata, and the notebook walks to it on purpose. What
the tests give us is not the idea. They give us a **safe switch** to it.
"""),

*game_step(GAME_SUM, GAME_FRAMES),

md("""\
`2 passed, 1 skipped`. The new design works for the old tests.

### 🔴 Red again

Remove the skip. The spare test must fail again, for the same reason as before.
"""),

ipytest_cell("""\
def test_spare_bonus_is_the_next_roll(game):
    game.roll(5)
    game.roll(5)   # spare
    game.roll(3)
    roll_many(game, rolls=17, pins=0)
    assert game.score() == 16
"""),

md("""\
`assert 13 == 16`. Same failure. Now the design lets us fix it in one place.

### 🟢 Green

In a frame with a spare, add the next roll as a bonus.
"""),

*game_step(GAME_FRAMES, GAME_SPARE),

md("""\
`3 passed`.

### 🔵 Refactor

Three things are not clear:

- In the program, the comment `# spare` explains the condition. A name is
  better than a comment: `_is_spare(first_roll)`.
- The number `10` now means "all the pins", and `FRAMES_PER_GAME` is also 10.
  The same number with two meanings is a trap. We give it a name: `ALL_PINS`.
- In the test, `roll(5); roll(5)` needs the comment `# spare`. A helper
  `roll_spare(game)` says it in the code.
"""),

*game_step(GAME_SPARE, GAME_SPARE_NAMED),

ipytest_cell("""\
def roll_spare(game):
    game.roll(5)
    game.roll(5)

def test_spare_bonus_is_the_next_roll(game):
    roll_spare(game)
    game.roll(3)
    roll_many(game, rolls=17, pins=0)
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

ipytest_cell("""\
def roll_strike(game):
    game.roll(10)

def test_strike_bonus_is_the_next_two_rolls(game):
    roll_strike(game)
    game.roll(3)
    game.roll(4)
    roll_many(game, rolls=16, pins=0)
    assert game.score() == 24
"""),

md("""\
This red is an `IndexError`, not a wrong number. The program still thinks
that each frame has 2 rolls. It counts the strike frame as "10 and 3", and it
looks for a 20th roll that does not exist.

### 🟢 Green

A strike frame scores 10 plus the next 2 rolls, and moves on by **1** roll.
"""),

*game_step(GAME_SPARE_NAMED, GAME_STRIKE),

md("""\
`4 passed`.

### 🔵 Refactor

Again a comment explains a condition. We give each idea a name:
`_is_strike`, `_strike_bonus`, `_spare_bonus` and `_pins_in_frame`. After this
step, `score()` reads like the rules at the top of this notebook.
"""),

*game_step(GAME_STRIKE, GAME_STRIKE_NAMED),

md("""\
`4 passed`. The refactor changed the structure, and the tests prove that the
behaviour stayed the same.

## 5 — A perfect game

**What we want next.** 12 strikes in a row: one for each of the 10 frames,
plus the 2 extra rolls of the 10th frame. Each frame scores 10 + 10 + 10 = 30.
The total is **300**.

This test checks two rules that the one-strike test does not reach. The bonus
of a strike is the next 2 **rolls**, also when those rolls are strikes in two
different frames. And the 2 extra rolls of the 10th frame are rolls, not
frames.

### 🔴 Red?
"""),

ipytest_cell("""\
def test_strike_bonus_uses_rolls_not_frames(game):
    roll_many(game, rolls=12, pins=10)
    assert game.score() == 300
"""),

md("""\
`5 passed`. **The new test passed at once.** There was no red step.

That can happen. The design from cycles 3 and 4 already handles it. But rule 1
says: a test that you never saw fail proves nothing. So we make it fail on
purpose. This is a **negative control**: we break the program in a known way,
and we check that the test sees it.

### 🔴 Negative control: a bonus of the next frame

A common mistake is to read the strike rule as "the bonus is the next
**frame**". For a strike followed by 3 and 4, that gives the same answer, so
the one-strike test cannot see the mistake. For a strike followed by a strike,
the next frame is only 10 pins, not 10 plus the roll after it.

We put this mistake into `_strike_bonus`, and keep the correct version so that
we can put it back. **Only the new test should fail.** If the one-strike test
also failed, the new test would add nothing.
"""),

ipytest_cell("""\
correct_strike_bonus = Game._strike_bonus

def strike_bonus_of_the_next_frame(self, first_roll):   # bug on purpose
    next_frame = first_roll + 1
    if self._is_strike(next_frame):
        return ALL_PINS             # forgets the roll after the second strike
    return self._pins_in_frame(next_frame)

Game._strike_bonus = strike_bonus_of_the_next_frame
"""),

md("""\
`1 failed, 4 passed`: `assert 200 == 300`. Only the perfect-game test sees the
mistake. So it can fail, and it checks a rule that no other test checks.

### 🟢 Green: put the correct code back
"""),

ipytest_cell("""\
Game._strike_bonus = correct_strike_bonus
del correct_strike_bonus, strike_bonus_of_the_next_frame
"""),

md("""\
`5 passed`. The kata is done.

## 6 — Change code that already exists

Until now, we wrote new code. At work, you often get code that somebody else
wrote, and you must change what it does. That is the situation of
`02_test_driven_development` in the legacy-refactor workshop. Here we practise
it on our own `Game`, and we pretend that we did not write it.

**The change request.** `score()` on a game that is not finished crashes with
`IndexError: list index out of range`. That message says nothing to the
caller. It must say: the game is not finished.

With code that you did not write, you do not start with the change. You start
with the question: **what does the code do now?**

### 🔍 Ask the code

We do not know what `score()` does after 3 rolls. So we write a test with a
guess, and we let the failure tell us the truth. This is a
**characterization test** (Michael Feathers, *Working Effectively with Legacy
Code*).
"""),

ipytest_cell("""\
def test_what_score_does_for_an_unfinished_game(game):
    roll_many(game, rolls=3, pins=4)
    assert game.score() == 12
"""),

md("""\
The guess was wrong: the reason is `IndexError`. Now we know the current
behaviour.

### 📌 Pin the current behaviour

We replace the guess with a test that records what the code does now, right or
wrong. It passes at once, and that is correct: we saw its failure one step
ago, and that failure taught us what to write. The probe test has done its
work, so we delete it.
"""),

ipytest_cell("""\
del test_what_score_does_for_an_unfinished_game

def test_unfinished_game_has_no_score(game):
    roll_many(game, rolls=3, pins=4)
    with pytest.raises(IndexError):
        game.score()
"""),

md("""\
`6 passed`. Now each test protects the current behaviour, also the behaviour
that we want to change.

### 🔵 Refactor: one place to change

The program reads `self._rolls[...]` in four methods. A check for missing
rolls would be needed in all four. So we first make one place where the rolls are
read: `_pins(roll)`. This changes the structure, not the behaviour. The pinned
test proves it: it still expects `IndexError`.
"""),

*game_step(GAME_STRIKE_NAMED, GAME_ONE_READ),

md("""\
`6 passed`.

### 🔴 Red: say what the new behaviour is

Change the test first. It now expects our own error, `IncompleteGameError`.

This is a change of behaviour. Code that catches `IndexError` from `score()`
breaks. In a real code base, find those callers before you make the change.
"""),

ipytest_cell("""\
def test_unfinished_game_has_no_score(game):
    roll_many(game, rolls=3, pins=4)
    with pytest.raises(IncompleteGameError):
        game.score()
"""),

md("""\
`NameError: name 'IncompleteGameError' is not defined`. Red.

### 🟢 Green

Add the error, and raise it in the one place that reads a roll.
"""),

*game_step(GAME_ONE_READ, GAME_FINISHED_CHECK),

md("""\
`6 passed`. The change is small, it sits in one place, and all old tests
still pass.

## What we have

The list of tests is the specification of the program. Each name says one
rule:
"""),

code("""\
print("\\n".join(name for name in list(globals()) if name.startswith("test_")))
"""),

md("""\
### What TDD gave us

- **A safe design change.** TDD did not invent the design. The list of rolls
  and the frame loop are the known answer to this kata. What the tests gave
  us: when the spare test showed that the first design did not fit, we could
  switch to a new design and know at once that nothing broke.
- **Small, checked steps.** We changed the `Game` class 8 times. After each
  change, all earlier tests ran again.
- **Tests that can fail.** Each test failed one time before we trusted it. The
  perfect-game test did not fail by itself, so we broke the program on purpose
  to see it fail.
- **A way to change code that you did not write.** Ask the code what it does,
  pin that behaviour, make one place to change, then change it test-first.

## Your turn

Do these with the same cycle: red, green, refactor.

**Exercise 1: a spare in the 10th frame.** 9 frames of 0 pins, then 5, 5, 3.
The score is 13. The test below passes at once. Write a negative control: break
the program in a way that you expect this test to catch. Which other tests
also fail? Then put the correct code back.
"""),

ipytest_cell("""\
def test_tenth_frame_spare_gets_one_bonus_roll(game):
    roll_many(game, rolls=18, pins=0)
    roll_spare(game)
    game.roll(3)
    assert game.score() == 13
"""),

md("""\
**Exercise 2: a real score sheet.** All three rules mixed, from a real game.
The score is 167. The test below passes at once too. Run the negative control
of station 5 again: this test also catches it. Find the frames that cause it.
"""),

ipytest_cell("""\
def test_a_real_score_sheet(game):
    for pins in [10, 7, 3, 9, 0, 10, 0, 8, 8, 2, 0, 6, 10, 10, 10, 8, 1]:
        game.roll(pins)
    assert game.score() == 167
"""),

md("""\
**Exercise 3: wrong input.** We decided: `roll()` refuses more pins than there
are, with a `ValueError`. The test is written, and it is red. Make it green,
then refactor. Then write the next test yourself: 2 rolls in one frame with
more than 10 pins together.
"""),

ipytest_cell("""\
def test_a_roll_of_more_than_all_pins_is_refused(game):
    with pytest.raises(ValueError):
        game.roll(ALL_PINS + 1)
"""),
]


def for_exercise(cell):
    """The exercise version of a cell, or None to leave the cell out."""
    if ANSWER not in cell.metadata.get("tags", []):
        return cell
    if cell.cell_type == "code":
        return code(YOUR_TURN)
    return None


def notebook(exercise):
    nb = nbf.v4.new_notebook()
    cells = header(exercise) + STATIONS
    if exercise:
        cells = [cell for cell in map(for_exercise, cells) if cell is not None]
    nb.cells = cells
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    return nb


for exercise, name in [(False, "bowling_kata.ipynb"), (True, "bowling_kata_exercise.ipynb")]:
    out = os.path.join(HERE, name)
    nb = notebook(exercise)
    nbf.write(nb, out)
    print("wrote", out, len(nb.cells), "cells")
