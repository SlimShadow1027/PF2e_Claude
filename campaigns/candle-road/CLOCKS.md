# Clocks — The Candle Road

Progress clocks: faction plans, looming threats, deadlines. The segment counts are canonical
in `state.json` (`clocks`); this file says what each clock *means* and what happens when it
fills.

Advance a clock with:

```
python3 tools/state.py --campaign candle-road clock advance "Clock name" 1
```

A clock marked **ticking** with a stated rate advances during an off-screen turn
(`system/18-between-session-prep.md`). A clock with no rate only advances in play.

## _Clock name_

- **Segments:** 0 / 6
- **Ticking:** no
- **Rate:** —
- **What it is:** _(what the world is doing)_
- **What the player can see:** _(what a rumour would reveal, if anything)_
- **What happens when it fills:** _(concretely — a scene, not a mood)_
- **What would slow or stop it:**

> **GM-ONLY**
>
> _(anything about this clock the player should not know)_
