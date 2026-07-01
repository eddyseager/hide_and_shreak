# Combined Code Review: Hide and Shreak

This review consolidates all previous feedback, ranked from critical game-breaking flaws to architectural polish.

## Priority 1: Critical Gameplay & Stability (Fix Immediately)

### 🔴 1. Missing Combat / Loss Condition
* **Location**: [move_to_player](file:///Users/tarski/Documents/rogue_engine/move.py#L20) in [move.py](file:///Users/tarski/Documents/rogue_engine/move.py)
* **Issue**: Player has no `Blocks_Movement` component, allowing enemies to walk directly onto the player's tile. Nothing happens when they overlap—no "game over", no health loss, no screaming.
* TODO - will implement later...

### 🔴 2. Crash Risks (IndexError & FileNotFoundError)
* **Location**: Global (`esper.get_components(...)[0]`) & [_change_level_down](file:///Users/tarski/Documents/rogue_engine/events.py#L41)
* **Issue**: Code blindly assumes the player always exists. If the player is removed, it throws an `IndexError`. If the player descends to a non-existent `.level` file, it crashes with a `FileNotFoundError`.
* TODO - fine for now since 2nd level doesnt have stairs down

### 🔴 3. "Wasted Turn" Wall-Bump Bug
* **Location**: [_move_player](file:///Users/tarski/Documents/rogue_engine/events.py#L34) in [events.py](file:///Users/tarski/Documents/rogue_engine/events.py)
* **Issue**: Moving into a wall correctly blocks physical movement but still consumes a turn (incrementing the counter and triggering enemies).
* Working as designed!
---

## Priority 2: Core Architecture & Performance (Refactor Soon)


### 🟠 5. O(N) Spatial Query Bottlenecks
* **Location**: [_blocks_movement](file:///Users/tarski/Documents/rogue_engine/move.py#L14) and [_spawn_at](file:///Users/tarski/Documents/rogue_engine/processors/spawn_enemy.py#L18)
* **Issue**: Both functions linearly scan all ECS components to check tile occupancy. With thousands of walls, this causes massive CPU slowdowns. The architecture requires an $O(1)$ 2D grid lookup.

### 🟠 6. File I/O on Level Transitions
* **Location**: [remove_level](file:///Users/tarski/Documents/rogue_engine/entities.py#L28) in [entities.py](file:///Users/tarski/Documents/rogue_engine/entities.py)
* **Issue**: The game destroys all positional entities and re-reads the `.level` text file from the hard drive every time the player uses stairs. Levels should persist in memory.

---

## Priority 3: Polish & Code Quality

### 🟡 7. Delayed Enemy Spawns
* **Issue**: Levels are 100% empty upon entry. Enemies only spawn after 20 turns, removing immediate tension.

### 🟡 8. Z-Order / Drawing Layers
* **Issue**: [Draw](file:///Users/tarski/Documents/rogue_engine/processors/draw.py#L5) renders overlapping entities in arbitrary ECS order. Floors might draw on top of items or enemies. A simple `layer` integer on the `Graphic` component is needed.

### 🟡 9. Naming & Shadowing
* **Issue**: `PlayerMover` incorrectly names the component that moves enemies. In `create_level`, the local variable `create_level` completely shadows the function name.

---

## Priority 4: Assets & Enhancements

*(No remaining issues)*

---

## ✅ Fixed Issues
* **Newline Parsing Bug**: Trailing newlines stripped in `load_level`.
* **Implicit Imports**: Explicitly imported `numpy` in `move.py`.
* **Unused Audio System**: Installed `pygame` dependency, initialized the mixer, and configured the game to play `music/gameplay.mp3` on an infinite loop at launch.
* **FOV Rendering Lag & Missing Processors**: Reordered drawing and FOV update systems to resolve rendering lag. Extracted enemy AI routing into a dedicated `Move_Enemy` processor with priority 6.
