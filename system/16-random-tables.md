# 16 — Random tables

Improv tables that `tools/roll.py table` rolls on for real:

```
python3 tools/roll.py table system/16-random-tables.md "Urban Rumors" --campaign X
python3 tools/roll.py table system/16-random-tables.md "What Goes Wrong" --count 2 --campaign X
python3 tools/roll.py table system/16-random-tables.md --list .
```

**Format:** numbered entries under a heading. `N. text` or `N-M. text`. The die size is the
highest number present, so a `1–20` table rolls a d20 and a `1–6` table rolls a d6. A rolled
result lands in the audit log tagged `table`, like any other roll.

Adding a table: put it under its own `###` heading with numbered entries. Nothing else is needed.

These are campaign-agnostic on purpose. Campaign-specific tables belong in
`campaigns/<slug>/WORLD.md`, which `roll.py table` will read just as happily.

---

## Names

### Human Names (Inner Sea)

1. Aleth Varnish
2. Harrow Kell
3. Semira Dann
4. Tobin Ashgrove
5. Ilse Radek
6. Corwin Pell
7. Marta Veyne
8. Denholm Rook
9. Odile Marchetti
10. Ferrin Lask
11. Beatrix Holm
12. Orval Cinders
13. Ysolde Brann
14. Casimir Vey
15. Nell Ardith
16. Tarquin Sale
17. Ruta Vohl
18. Emeric Tash
19. Perrin Dole
20. Alvina Stroud

### Dwarf Names

1. Brunhild Ironbraid
2. Dagmar Stonewell
3. Orik Hammerfast
4. Vesta Copperlode
5. Thrain Deepdelve
6. Hilde Anvilsong
7. Gorm Slagheart
8. Rurik Grimvault
9. Astrid Orebound
10. Balin Coalmarrow
11. Sigrun Truehammer
12. Dolf Emberhand

### Elf Names

1. Caelith Morrow
2. Ysandriel Thorn
3. Faelan Quiet-Water
4. Nimue Silverash
5. Aeldric Vane
6. Serath Duskmere
7. Lirien Hollowsong
8. Thaeloth Grey
9. Elowen Farstride
10. Maruvel Nightglass
11. Sylvain Ashwither
12. Ithiliel Crowe

### Goblin, Kobold and Orc Names

1. Nub Sharpsticks
2. Wex Rattlebone
3. Irritation Grimes
4. Skiv the Persuasive
5. Meepo Longclaw
6. Vashk Emberscale
7. Ozgra Bonesplit
8. Hrud Two-Axe
9. Yikkit Fastfoot
10. Grulla Greasefinger
11. Sszarn Dustwing
12. Karg the Regrettable

### Halfling and Gnome Names

1. Pim Tolliver
2. Bexley Fernwhistle
3. Dimble Crackpop
4. Rosamund Applewhite
5. Fizwick Glimmerbutton
6. Tansy Underbough
7. Nim Quicklatch
8. Orsolya Pinbright
9. Wendel Teacake
10. Zizzle Marchwind
11. Poppy Cobbleknock
12. Fenwick Tallow

### Place Names

1. Greywater Crossing
2. The Drowned Cat (an inn)
3. Ashfall
4. Thorn Vigil
5. Nine Widows
6. Saltpath
7. The Unmended Gate
8. Low Cinder
9. Bellrot
10. Maiden's Fault
11. Copperleap
12. The Long Quiet
13. Hollowmarch
14. Dunn's Regret
15. Kettlewash
16. The Scoured Steps
17. Candlemire
18. Oldwrack
19. Thistledown Ferry
20. The Weeping Arch

---

## NPCs

### NPC Quirks

1. Never finishes a sentence about themselves.
2. Counts things aloud under their breath.
3. Refuses to sit with their back to a door.
4. Gives everyone a nickname within a minute of meeting them.
5. Keeps touching a ring that clearly is not theirs.
6. Laughs a beat after everyone else.
7. Answers questions with questions when nervous.
8. Speaks about themselves in the third person when lying.
9. Carries something entirely useless everywhere.
10. Will not say a particular name out loud.
11. Corrects other people's grammar, badly.
12. Flinches at sudden kindness.
13. Eats constantly, and offers you some.
14. Claims to have met every famous person mentioned.
15. Cannot stop apologising for the weather.
16. Hums a tune with no ending.
17. Overexplains simple things, precisely.
18. Watches your hands rather than your face.
19. Keeps a tally of grudges, written down.
20. Is much older or younger than they look, and knows it.

### NPC Wants

1. To be believed about something nobody believes.
2. Out — of the city, the trade, the marriage, the debt.
3. A body back, or a grave found.
4. The respect of one specific person.
5. Somebody else to make the decision.
6. Their old job, and the standing it came with.
7. To stop being afraid of one particular thing.
8. Money, urgently, for a reason they will not give.
9. To finish something a dead person started.
10. To be left alone, and to be asked first.
11. A witness. Just one, who will say what they saw.
12. To pass something on before they cannot.
13. Revenge, but they have not decided on whom.
14. To be useful again.
15. Proof they were right all along.
16. Something to worship that answers.
17. Someone to inherit what they built.
18. For the party to leave, before they are noticed with them.
19. An apology they will never ask for.
20. To know what happened. Not to fix it. Just to know.

### NPC First Impressions

1. Too pleased to see you.
2. Openly calculating what you are worth.
3. Exhausted past the point of caring.
4. Performing calm, badly.
5. Genuinely, unsettlingly kind.
6. Mid-argument with someone who has just left.
7. Busy, and making sure you see it.
8. Recognises one of you, and hides it.
9. Drunk, and sharper for it.
10. Afraid of something in the room, not of you.
11. Bored, and looking for entertainment at your expense.
12. Warm to one of you and cold to the rest.

---

## Settlements and scenes

### Tavern Details

1. The fire is out and nobody has mentioned it.
2. Someone is asleep at the best table and everyone works around them.
3. The ale is good, the food is a threat.
4. A dog that belongs to nobody and rules the place.
5. Two prices: one posted, one for you.
6. A wall of names, some crossed out.
7. Musicians who are practising, not performing.
8. A back room with a closed door and a bored guard.
9. Rain coming in exactly one place, marked with a bucket.
10. Everybody stops talking. Then starts again, quieter.
11. A game in progress with stakes that are clearly not coins.
12. The innkeeper is not the one in charge.

### Settlement Details

1. Every door on one street is painted the same colour, recently.
2. The well is chained shut.
3. Children's chalk drawings all show the same shape.
4. A market with three stalls and eleven empty frames.
5. The temple bell is missing.
6. Someone is being watched, and everyone is pretending not to notice.
7. New graves, more than the season should give.
8. A guard post built facing into the town.
9. Notices nailed over older notices, six deep.
10. The smell of something industrial, and nobody will name it.
11. A shrine to a god nobody here worships, kept immaculately.
12. A street that is walked around rather than down.

### Urban Rumors

1. A tax collector has not been seen in nine days, and the ledgers went with them.
2. The river ran red for an hour and the priests have stopped explaining it.
3. Someone is paying for grave dirt. In coin. No questions.
4. The night watch has stopped walking the eastern wall and will not say why.
5. A child's song names a street that is not on any map.
6. The guild master's new partner has no history anyone can find.
7. Three houses on the same street have sold in a month, all to the same buyer.
8. The lamplighter has started skipping a lamp.
9. Dogs will not go down to the docks after dark.
10. A physician is turning patients away with money in their hands.
11. There is a second set of keys to the granary and the council does not have them.
12. Someone has been leaving food at the old shrine, and something has been eating it.

### Wilderness Details

1. A cairn, recently added to.
2. Birds absent for a mile, then suddenly everywhere.
3. A road that is better maintained than it should be.
4. Trees blazed with a mark that is not a forester's.
5. A stream running the wrong way for the slope.
6. An old battlefield, tidied.
7. Something large has been dragged, and recently.
8. A shepherd's hut with the door barred from outside.
9. Frost in a place with no reason for frost.
10. A shrine with fresh offerings and no path to it.
11. Weather that stops at a line you can see.
12. Hoofprints that end.

### Dungeon Dressing

1. A door opened and wedged by someone in a hurry, long ago.
2. Water damage from below rather than above.
3. Writing at ankle height, in a hand that was lying down.
4. A room cleaned and maintained, in the middle of ruin.
5. Sconces with no torches, and no soot.
6. A floor swept in one direction only.
7. Rubble stacked, not scattered.
8. A chair facing a blank wall.
9. Bones with the wrong number of joints.
10. Every hinge oiled.
11. A tally scratched by the door, stopping mid-count.
12. Something's droppings, and something else's, and they are avoiding each other.
13. A mural with one figure scratched out, thoroughly.
14. Fresh air from a direction with no opening.
15. A coin, old, on the threshold — and another, further in.
16. Silence that is being maintained rather than merely present.

---

## Weather

### Weather — Temperate, Spring or Autumn

1. Clear and cold at dawn, warm by noon.
2. Overcast, still, and oddly loud.
3. Rain from mid-morning; the road turns.
4. Fog to fifty feet until the sun burns it off.
5. Wind hard enough to make ranged attacks a decision.
6. Bright and blustery, clouds moving fast.
7. Drizzle that never quite stops.
8. A storm in the afternoon, visible coming for an hour.
9. Unseasonal warmth, and everyone remarking on it.
10. Cold rain, then a hard clear night.
11. Mist that rises from the ground rather than settling.
12. Perfect weather, which nobody trusts.

### Weather — Temperate, Summer

1. Hot and still; travel is half pace by afternoon.
2. Heat, then a thunderstorm that clears nothing.
3. Bright, dry, and dusty.
4. Humid; everything sticks, tempers included.
5. Overcast and warm; good travel.
6. A clear day with a hot wind off the south.
7. Rain at last, and it lasts an hour.
8. A heat haze that makes distances lie.
9. Cool, bright, and windy — the best day of the season.
10. A dry storm: lightning, no rain, and a fire risk.
11. Oppressive. Everyone is short with everyone.
12. Cloudless, and too hot to travel past noon.

### Weather — Temperate, Winter

1. Hard frost, clear sky, bitter wind.
2. Snow overnight; the road is guesswork.
3. Grey, damp, and just above freezing. The worst kind.
4. Clear and windless; cold that gets in anyway.
5. Sleet.
6. A thaw, and mud to the ankle.
7. Freezing fog; visibility to twenty feet and everything glazed.
8. Heavy snow, still falling, travel a third pace.
9. Bright, hard cold, and beautiful.
10. Ice storm; every surface treacherous.
11. Wind that finds every gap.
12. A still, warm day in the middle of it, and something has woken up.

### Weather — Arid

1. Clear, hot, and windless.
2. A dust wind from before dawn.
3. Killing heat; travel at night or not at all.
4. Overcast, and the temperature drops thirty degrees.
5. A sandstorm, an hour out and closing.
6. Cool morning, brutal afternoon, freezing night.
7. Rain, briefly, and the ground will not take it.
8. Haze that hides the horizon.
9. A wind that does not stop for two days.
10. Clear and merely warm. A gift.

### Weather — Cold or Highland

1. Snow above, clear below.
2. Whiteout for six hours.
3. Cold, clear, and thin-aired.
4. Wind off the ice, carrying grit.
5. A break in the weather; move now.
6. Freezing rain at altitude.
7. Avalanche conditions on any slope.
8. Sun on snow; bright enough to hurt.
9. Cloud below you, and clear above.
10. Still, silent, and dangerously cold.

### Weather — Coastal or Nautical

1. Fair wind, following sea.
2. Becalmed.
3. Fog on the water, no wind.
4. Squalls all day, each an hour apart.
5. A steady gale, and good speed if you dare it.
6. Cross-sea; everything is harder and slower.
7. A storm building to the west, four hours out.
8. Clear, cold, and a wind on the beam.
9. Heavy swell under a clear sky — something happened elsewhere.
10. The tide is wrong.

---

## Encounters

### Urban Encounters (levels 1–4)

1. A pickpocket, already caught by someone else.
2. Two guards shaking down a stallholder; a decision, not a fight.
3. A cutpurse gang of three, and one of them wants out.
4. A body in an alley, still warm, and a witness leaving fast.
5. A stray beast in the market — frightened, not hostile.
6. A press gang recruiting hard.
7. A funeral procession that blocks the way and must not be interrupted.
8. A debt collector who recognises one of the party.
9. A cellar flooded, and a voice in it.
10. Somebody following, badly.
11. A fire, spreading, and no watch yet.
12. A cult handbill, and the person handing them out is earnest.
13. A duel about to start over nothing.
14. A child who has stolen something dangerous.
15. A wagon overturned across the road, deliberately.
16. A rival adventuring party, lighter on ethics.
17. A creature out of the sewers, in daylight, which is wrong.
18. A guard officer looking for exactly the sort of people the party are.
19. A merchant with a proposition and no time to explain.
20. Nothing at all — but the street is empty and should not be.

### Urban Encounters (levels 5–10)

1. A faction enforcer with a name and a message.
2. An assassination in progress, and the target is useful.
3. A district cordoned off by armed men in no livery.
4. A summoned thing loose, and its summoner nearby and panicking.
5. A riot forming; ten minutes to decide what side of it to be on.
6. A noble's carriage, stopped, and an invitation extended.
7. A plague house, marked, and someone alive inside.
8. Corrupt watch running a shakedown with real force behind it.
9. Something in the sewers has come up through a cellar floor.
10. A rival who has been hired specifically to stop the party.
11. A hostage situation with a stupid, sympathetic cause.
12. A magical accident in a workshop, still going.
13. An arrest warrant, wrongly issued, in earnest hands.
14. A creature disguised as a person the party know.
15. A bridge sabotaged, and the saboteur still on it.
16. A shipment arriving that several parties want.
17. A duel of honour that the party is being used to witness.
18. A sending, a summons, or a very expensive messenger.
19. A cult ceremony half an hour from completion.
20. The city's own defences turning on a district.

### Wilderness Encounters (levels 1–4)

1. Tracks crossing the road, fresh, large.
2. A merchant caravan, nervous, willing to pay for company.
3. Wolves, hungry, and a choice about whether to make it a fight.
4. A bandit toll, four of them, negotiable.
5. A trapper's line, and something in it that should not be.
6. A collapsed bridge and a long way round.
7. A pilgrim travelling alone, and lying about why.
8. A swarm of something small and biting.
9. A shepherd missing animals, and afraid to say what to.
10. Standing stones, and something left at them this morning.
11. A hunting party from somewhere with unfriendly laws.
12. A wounded creature, dangerous and pitiable.
13. Smoke, a mile off, from a place that should not be burning.
14. A ford that has risen since the map was drawn.
15. A cave mouth, and cold air coming out of it.
16. A scarecrow, in a field with nothing planted.
17. Two groups about to fight, and neither has seen the party.
18. An old road, better than the new one, going the wrong way.
19. A camp, recently left, in a hurry.
20. Weather closing in, and no shelter for three hours.

### Wilderness Encounters (levels 5–10)

1. A territorial predator well above the party's weight.
2. A war band moving with purpose, and a scout who has seen the party.
3. A druid circle that considers the party the problem.
4. A wyvern, or worse, hunting the road.
5. A ruin with a new door in it.
6. A river crossing held by something that takes tolls in a different currency.
7. A giant's cairn, and the giant returning.
8. A plague of something unnatural moving through the livestock.
9. An enemy patrol with a tracker good enough to follow.
10. A dying messenger with a real message.
11. A rift, a rent, or a place the air is wrong.
12. A hunting party from a plane that is not this one.
13. A village that has been emptied, tidily.
14. A caravan taken; the survivors are the problem.
15. A sacred place being desecrated, in progress.
16. Something enormous asleep across the only pass.
17. A rival expedition, ahead of the party, and leaving traps.
18. A storm with something inside it.
19. A herd stampeding toward the party, driven.
20. A stranger who knows the party's names.

### Dungeon Encounters (levels 1–4)

1. Scavengers, startled, and deciding.
2. A patrol on a schedule the party could learn.
3. A trap already sprung on somebody else.
4. Something feeding, and territorial about it.
5. Two factions of inhabitants, and an opportunity.
6. A prisoner, and a reason to doubt them.
7. A door that has been barred from the far side.
8. A collapse, and something on the other side of it digging.
9. A guardian that asks a question first.
10. Vermin in numbers that make a real fight.
11. A scout who will run and report rather than fight.
12. A shrine, active, and its attendant.

### Dungeon Encounters (levels 5–10)

1. A guardian construct that has outlived its instructions.
2. A hunting pair that works as a pair.
3. An ambush set for the party specifically.
4. A ritual in progress with rounds left on it.
5. A thing sealed in, and the seal failing.
6. The dungeon's owner, who would rather negotiate.
7. A flooded level, and something native to it.
8. An enemy spellcaster with a prepared battlefield.
9. Something that has been imitating one of the inhabitants.
10. A rival party, further in, in trouble.
11. A room that is itself the encounter.
12. Something that wakes when the light reaches it.

---

## Complications and consequences

### What Goes Wrong

1. It works, but it takes twice as long and someone notices.
2. The wrong person finds out.
3. It breaks. Not now — later, at the worst moment.
4. Someone else wanted it, and is still in the building.
5. It works perfectly, and the result is not what was wanted.
6. A debt is created, to someone unwelcome.
7. Noise. A great deal of noise.
8. The information was true when it was given.
9. An ally is compromised by association.
10. It costs money that was already spent.
11. The route out is no longer the route in.
12. Somebody is hurt who was not part of this.
13. A thing that was sealed is now merely closed.
14. The reward exists, and is not portable.
15. Time passes — more than it should have.
16. A promise has to be made to finish it.
17. It attracts something's attention.
18. The evidence survives, with the party's name on it.
19. The problem is solved and the cause is not.
20. It worked. Nobody will believe it.

### Skill Check Failure Complications

1. It takes ten times as long.
2. It works, but something breaks doing it.
3. A tool, a component, or a consumable is spent.
4. Loud. Whatever was nearby now knows.
5. You are hurt doing it — minor, persistent, annoying.
6. You learn something false and believe it.
7. It half works; the rest needs a second attempt at a worse DC.
8. Someone sees you do it.
9. You succeed and leave obvious evidence.
10. You cannot try again today.
11. It works for someone else, later, and not for you.
12. You get what you asked for, exactly and unhelpfully.

### Treasure Flavour

1. Coin from three countries, none of them this one.
2. Wrapped in a child's cloak.
3. Still warm.
4. Marked with a house sigil somebody will recognise.
5. Buried in the floor, badly, recently.
6. In a purse with a name stitched inside.
7. Counted and tallied, with the tally present.
8. Half of it is missing and the space is obvious.
9. Beautiful, and worth less than it looks.
10. Ugly, and worth more.
11. Cursed is too strong a word. Unlucky is about right.
12. Somebody is coming back for this.

---

## Oracle tables

Used by `tools/oracle.py meaning`. See `19-solo-oracle.md`.

### Oracle Actions

1. Abandon
2. Betray
3. Bind
4. Break
5. Carry
6. Conceal
7. Corrupt
8. Defend
9. Delay
10. Demand
11. Deny
12. Divide
13. Escape
14. Exchange
15. Expose
16. Follow
17. Gather
18. Guard
19. Hunt
20. Imitate
21. Inherit
22. Invite
23. Mend
24. Mislead
25. Mourn
26. Obstruct
27. Offer
28. Open
29. Overreach
30. Persuade
31. Postpone
32. Preserve
33. Provoke
34. Pursue
35. Reclaim
36. Refuse
37. Release
38. Remember
39. Repay
40. Replace
41. Reveal
42. Sacrifice
43. Seal
44. Search
45. Seize
46. Serve
47. Signal
48. Summon
49. Surrender
50. Survive
51. Swear
52. Take
53. Test
54. Threaten
55. Trade
56. Transform
57. Trap
58. Trust
59. Undo
60. Warn
61. Watch
62. Weaken
63. Withdraw
64. Witness
65. Yield
66. Await
67. Bargain
68. Build
69. Burn
70. Claim
71. Cleanse
72. Confess
73. Confront
74. Consume
75. Counterfeit
76. Deceive
77. Dig
78. Dismantle
79. Dispute
80. Elevate
81. Enlist
82. Erase
83. Falter
84. Forge
85. Fortify
86. Gamble
87. Harvest
88. Hide
89. Hold
90. Honour
91. Infiltrate
92. Interrupt
93. Judge
94. Lead
95. Lose
96. Name
97. Petition
98. Recruit
99. Return
100. Wait

### Oracle Themes

1. Abundance
2. Ambition
3. Ancestry
4. Appetite
5. Authority
6. Balance
7. Beauty
8. Belief
9. Betrayal
10. Blood
11. Boundary
12. Burden
13. Ceremony
14. Change
15. Compromise
16. Consequence
17. Craft
18. Debt
19. Decay
20. Defence
21. Desire
22. Destiny
23. Disease
24. Distance
25. Duty
26. Endurance
27. Exile
28. Faith
29. Famine
30. Fear
31. Fertility
32. Freedom
33. Grief
34. Guilt
35. Health
36. Hierarchy
37. History
38. Home
39. Hope
40. Hunger
41. Identity
42. Innocence
43. Inheritance
44. Isolation
45. Justice
46. Kinship
47. Knowledge
48. Labour
49. Language
50. Law
51. Loyalty
52. Machinery
53. Madness
54. Memory
55. Mercy
56. Migration
57. Nature
58. Obligation
59. Obsession
60. Order
61. Ownership
62. Passage
63. Patience
64. Peace
65. Pestilence
66. Poverty
67. Power
68. Pride
69. Prophecy
70. Protection
71. Punishment
72. Purity
73. Reputation
74. Revenge
75. Ritual
76. Rot
77. Sacrifice
78. Sanctuary
79. Secrecy
80. Shame
81. Silence
82. Sleep
83. Sorcery
84. Sovereignty
85. Stagnation
86. Starvation
87. Strength
88. Superstition
89. Survival
90. Territory
91. Time
92. Trade
93. Tradition
94. Trust
95. Truth
96. Tyranny
97. Violence
98. Water
99. Wealth
100. Wilderness

### Oracle Descriptors

1. Abandoned
2. Adorned
3. Ancient
4. Angry
5. Armoured
6. Bloodied
7. Borrowed
8. Bright
9. Broken
10. Buried
11. Burning
12. Careful
13. Charred
14. Cheap
15. Clean
16. Cold
17. Concealed
18. Confined
19. Contested
20. Corrupted
21. Counterfeit
22. Cracked
23. Crowded
24. Dangerous
25. Dark
26. Deep
27. Delicate
28. Deliberate
29. Diminished
30. Disputed
31. Drowned
32. Dry
33. Elaborate
34. Empty
35. Exposed
36. Faded
37. Familiar
38. Flooded
39. Forbidden
40. Forgotten
41. Fortified
42. Fragile
43. Fresh
44. Frozen
45. Growing
46. Guarded
47. Half-finished
48. Heavy
49. Hidden
50. Hollow
51. Holy
52. Hot
53. Hungry
54. Immaculate
55. Improvised
56. Inherited
57. Isolated
58. Loud
59. Luminous
60. Makeshift
61. Marked
62. Modest
63. Mouldering
64. Narrow
65. New
66. Obscured
67. Old
68. Ornate
69. Overgrown
70. Patched
71. Plain
72. Poisoned
73. Precise
74. Quiet
75. Rebuilt
76. Repaired
77. Reserved
78. Rotten
79. Ruined
80. Sealed
81. Shared
82. Sharp
83. Silent
84. Slow
85. Smoky
86. Stained
87. Stolen
88. Sudden
89. Sunken
90. Sweet
91. Tangled
92. Temporary
93. Thin
94. Unfinished
95. Unlit
96. Unwanted
97. Warm
98. Wet
99. Withered
100. Worn

### Oracle Focuses

1. A bargain
2. A body
3. A boundary
4. A bridge
5. A burden
6. A cage
7. A child
8. A choice
9. A corpse
10. A crowd
11. A debt
12. A door
13. A family
14. A feast
15. A field
16. A fire
17. A gate
18. A grave
19. A guard
20. A guild
21. A harvest
22. A herd
23. A key
24. A ladder
25. A ledger
26. A letter
27. A lie
28. A light
29. A list
30. A lock
31. A map
32. A mark
33. A market
34. A meal
35. A message
36. A mine
37. A mirror
38. A name
39. A path
40. A price
41. A prisoner
42. A promise
43. A ritual
44. A river
45. A road
46. A rope
47. A ruin
48. A seal
49. A secret
50. A shrine
51. A signature
52. A song
53. A stair
54. A stone
55. A storm
56. A stranger
57. A threshold
58. A tomb
59. A tool
60. A tower
61. A trade
62. A trail
63. A tree
64. A wall
65. A weapon
66. A well
67. A wound
68. An animal
69. An arch
70. An army
71. An heir
72. An illness
73. An oath
74. An offering
75. An official
76. An order
77. The border
78. The cellar
79. The city
80. The council
81. The crossing
82. The dark
83. The dead
84. The docks
85. The faithful
86. The forge
87. The garrison
88. The library
89. The mountain
90. The night
91. The plague
92. The quarry
93. The road
94. The sea
95. The season
96. The temple
97. The tide
98. The treasury
99. The watch
100. The winter
