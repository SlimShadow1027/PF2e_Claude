# {{CAMPAIGN_TITLE}}

- **Slug:** {{CAMPAIGN_SLUG}}
- **Created:** {{CREATED_DATE}}
- **System:** {{SYSTEM}}
- **World:** none
- **Era:** {{ERA}}
- **Start date:** {{START_DATE}}
- **Shape:** {{SHAPE}}
- **Expected level range:** {{LEVEL_RANGE}}
- **Advancement:** {{ADVANCEMENT}}
- **Genre:** {{GENRE}}
- **Tone:** {{TONE}}
- **Lethality:** {{LETHALITY}}
- **Setting:** {{SETTING}}

> `System:` is **{{SYSTEM_NAME}}** and decides which rules documents and which tables apply.
> It must match `"system"` in `state.json`; `tools/validate.py` fails the campaign if they
> disagree, and `state.json` wins. Changing it means rebuilding the characters.
> `python3 tools/rules.py which {{CAMPAIGN_SLUG}}`.
>
> `World:` names a folder under `worlds/`, or `none` for a standalone campaign. A campaign
> with `World: none` behaves exactly as it does today — nothing about the shared layer
> becomes mandatory. See `system/21-shared-worlds.md`. A world may hold campaigns of **both**
> rulesets; see `system/23-cross-system-worlds.md`.

## The pitch

{{PITCH}}

## Premise and stakes

- **What is wrong with the world:** {{PREMISE}}
- **Who is causing it:** {{ANTAGONIST}}
- **What happens if nobody stops it:** {{STAKES}}

## Protagonist framing

Why is this character the one who acts?

{{PROTAGONIST_FRAMING}}

## Party structure

- **Characters the player controls:** {{PLAYER_CHARACTERS}}
- **Characters the GM runs:** {{GM_CHARACTERS}}
- **Ally status:** {{ALLY_STATUS}}

See `system/03-difficulty-and-solo-levers.md` for what each party shape does to the math.

## Setting assumptions kept

| Assumption | Decision |
|---|---|
| Gods and religion | {{ASSUMPTION_GODS}} |
| Planes and afterlife | {{ASSUMPTION_PLANES}} |
| Ancestries / species present | {{ASSUMPTION_ANCESTRIES}} |
| Calendar | {{CALENDAR}} |
| Magic prevalence | {{ASSUMPTION_MAGIC}} |
| Technology level | {{ASSUMPTION_TECH}} |

## Themes to keep returning to

{{THEMES}}

## Intake answers not captured above

{{INTAKE_NOTES}}
