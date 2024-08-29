# Shapes And Tiles

# Overview and Objective
The board consists of a 3x3 grid of randomly selected Tiles. Players place their resources (shapes) on the Tiles to rule them and get various benefits. The objective is to have the most points at the end of the game.

End conditions:
1. All tiles have a ruler at the end of a round
2. At the end of the 6th round

## Gameplay

Rounds consist of alternating turns between players. On a player's turn, they may take one of these actions:

1. Place a shape from their bank on to a tile
2. Use a tile
3. Use a powerup
4. Pass 

After passing, a player may not take any more actions that round (they can still react). If they're the first player to pass in a round, they become first player for the next round. A round ends when both players have passed. 

## Shape Hierarchy/Power

Shapes have power levels:

```
Triangles: 3
Squares: 2
Circles: 1
```

Stronger shapes can be placed on top of weaker ones. This is called trumping. When this happens, the weaker shape is removed from the slot it was on. It may be placed by the owner in their graveyard.

## Graveyard
Each player has 3 different powers in their graveyard. They're similar to tiles. Shapes are placed on them, and they give various boons.

## Tiles

**Ruling a tile:** Each tile has some criteria which determines who rules the tile (can be no one). This normally gives a benefit to the ruler. 

**Presence:** A player is present at a tile if they have a shape there. Your **presence** is the total number of tiles you are present at.

**Power at Tiles:** Each player has a power-level at a tile. It comes from the sum of the power of their shapes there. Your **peak power** is the highest power you have across all tiles.

**Cooldowns:** Many tiles have a cooldown (the description will say "once per round"). Cooldowns are _shared_ between players. I.e. once a tile is on cooldown, it may not be used by anyone.

## Base-Income
At the start of each round, players produce 1 of each shape.

## Round Bonuses
At the end of each round, rewards are given to players if they fulfill some condition.

## Conversions
At any time on a player's turn, they may perform conversions within their bank. Conversions do not count as an action. When converting weaker shapes to stronger ones, the rate is 3 to 1. When converting stronger to weaker, it is 1 to 1.

## Miscellaneous/Terms

When multiple tiles are resolving effects at the same time, they happen in this order:

```
1 2 3
4 5 6
7 8 9
```
Some tiles use **adjacency**. In the above grid, 1 is adjacent to 2 and 4.

When both players are due to resolve some effect at the same time, the first player resolves them first. 

Some Tiles have effects that happen at the end of a round. These resolve before round bonuses.

**Producing** a shape adds it to your bank.

**Burning** a shape removes it. It does not go to the graveyard.

**Receiving** a shape always happens at an empty slot on a tile. If there are no empty slots at that tile, no shape is received. 

When **Moving** a shape, it must also go to an empty slot.

A **set** is 1 circle, 1 square, and 1 triangle

A **pair** is any 2 shapes