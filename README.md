# Hide and Shreak

A Python roguelike demo where your only objective is survival: run away, escape danger, and try and escape the dungeon.

---

## Controls

* **Arrow Keys**: Move in four cardinal directions (Up, Down, Left, Right)
* **`<` / `>`**: Descend or ascend stairs between dungeon levels

---

## Getting Started

This project relies on [`uv`](https://github.com/astral-sh/uv) for fast, reliable Python environment and dependency management.

### Prerequisites

Ensure you have `uv` installed on your system. If you haven't installed it yet:

```bash
# macOS/Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

You can launch the game straight from GitHub without cloning the repository:

`uvx --from git+https://github.com/eddyseager/hide-and-shreak.git hide-and-shreak`

or clone the repository and run `uv run src/main.py`
