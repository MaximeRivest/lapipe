# lapipe

*A tiny, zero-dependency “value-first” pipe helper for Python &nbsp;—&nbsp; inspired by Unix pipes and F#’s `|>`, but with an optional `_` placeholder so you can drop the value exactly where you need it.*

[![PyPI](https://img.shields.io/pypi/v/lapipe?color=%2337c)](https://pypi.org/project/lapipe/)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

---

## Why?

* Chain data-transform steps **without** intermediate variables  
* Keep **left-to-right** reading order (like functional pipes)  
* Explicitly mark the slot with `_` **only when you need to**  
* Works with any callables — Pandas, NumPy, matplotlib, your own functions — no monkey-patching or heavy frameworks

---

## Installation

```bash
pip install lapipe
````

---

## Quick start

```python
from lapipe import pipe, _

def add(a, b):      return a + b
def mul(a, b):      return a * b

result = (
    pipe(2)               # wrap the value
    | (add, 3)            # 2 -> first arg: add(2, 3)
    | (mul, 4, _)         # 5 -> second arg: mul(4, 5)
)
print(result.value)        # 20
```

### Rules in one table

| syntax  | how the value is passed  |                         |
| ------- | ------------------------ | ----------------------- |
| \`      | func\`                   | first positional arg    |
| \`      | (func, \*args)\`         | first positional arg    |
| \`      | (func,  …, \_)\`         | replaces that `_`       |
| \`      | (func, {..., k=\_})\`    | replaces that kwarg `_` |
| returns | **new `Pipe`** each step |                         |

---

## Examples

### 1. NumPy vector math

```python
import numpy as np
from lapipe import pipe, _

vec = np.arange(5)                # [0 1 2 3 4]

out = (
    pipe(vec)
    | (np.add, 10)                # [10 11 12 13 14]
    | (np.multiply, 2, _)         # [20 22 24 26 28]
    | (np.power, _, 2)            # square each
)
print(out.value)
# [400 484 576 676 784]
```

### 2. Pandas transformation + plot

```python
import pandas as pd, matplotlib.pyplot as plt
from lapipe import pipe, _

df = pd.DataFrame({
    "year": range(2010, 2025),
    "sales": [42, 45, 47, 44, 50, 54, 57, 60, 64, 66, 70, 74, 78, 81, 85]
})

(
    pipe(df)
    | (pd.DataFrame.copy, _)              # keep original intact
    | (pd.DataFrame.set_index, _, "year")
    | (pd.DataFrame.assign, growth=lambda d: d.sales.pct_change())
    | (pd.DataFrame.rolling, 3)           # 3-year moving mean
    | (pd.core.window.Rolling.mean, _)    # computes .mean()
    | (pd.DataFrame.plot, _, y="sales")   # `_` is DataFrame here
)
plt.title("3-year moving average sales")
plt.show()
```

### 3. Keyword placeholder

```python
def greet(who, *, punct="!"):
    return f"Hello {who}{punct}"

pipe("?") | (greet, "world", {'punct': _})
# Pipe('Hello world?')
```

---

## API

```python
pipe(value)        # wrap any value → returns Pipe
Pipe | func        # call func(value, …)
Pipe | (func, ...) # tuple form with args / kwargs
_                  # sentinel placeholder
Pipe.value         # access the wrapped result
```

That’s it! No other symbols, no hidden globals.

---

## Design notes

* **No string → AST tricks.** Just normal Python calls.
* **No runtime import hacks.** You decide which libraries to use.
* **Stateless.** Each step returns a *new* `Pipe`; the original stays unchanged.
* **Pure Python 3.8+.** One file, \~80 lines.

---

## Contributing

Issues and PRs are super welcome!
If you find an edge-case that breaks the placeholder logic (looking at you, Pandas & NumPy dtypes), open an issue or send a failing test.

```bash
git clone https://github.com/yourname/lapipe
pytest
```

---

## License

MIT — do what you want, just keep the copyright and don’t blame us.

---

> Designed so your data can flow like water, not spaghetti. Enjoy piping! 🚰

