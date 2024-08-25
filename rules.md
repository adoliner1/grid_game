# Shapes And Tiles

# Overview
The board consists of a 3x3 grid of Tiles. Players place their resources (shapes) on the tiles. Tiles offer various benefits such as income, points, utility, etc. There is also a powerups section below the 3x3 grid.

## Objective
Have the most points at the end of the game. The game ends either when:
1. All tiles have a ruler at the end of a round
2. At the end of the 6th round
## Gameplay

Rounds consist of alternating turns between players. On a player's turn, they may take one of these actions:

1. **Place a shape from storage onto a slot on a tile.** Shapes have power levels (see below). Stronger shapes can be placed on top of weaker shapes, removing the weaker shape from the tile. This is called trumping. The weaker shape which was removed may be placed by the owner in their Powerups section
2. **Use a tile**.
3. **Use a powerup.**
4. **Pass**. After passing, a player may not take any more actions that round (they can still react). If they're the first player to pass in a round, they become first player for the next round.

A round ends when both players have passed. 

## Shape Hierarchy/Power

Triangles: 3
Squares: 2
Circles: 1

## Base-Income
At the start of each round, players produce (in their storage) 1 of each shape.

## Ruling
Each tile has some criteria which determines who rules that tile (if anyone). The ruler gains some benefit (normally) from being ruler. 

## Presence
You are present at a tile if you have a shape there. Your **presence** is the total number of tiles you are present at.

## Power
Players have power at each tile. It comes from the sum of the power of their shapes there. Your **peak power** is the highest power you have across all tiles.

## Round Bonuses
Rewards are given to players that fulfill a condition at the end of each round.

## Conversions
At any time on a player's turn, they may perform conversions with their shapes in storage at the following rates. Performing a conversion does not count as performing an action:

- 3 circles to 1 square
- 3 squares to 1 triangle
- 1 square to 1 circle
- 1 triangle to 1 square

## Miscellaneous

When multiple tiles are resolving effects at the same time, they happen in this order:

```
0 1 2 
3 4 5 
6 7 8
```

When both players are due to resolve some effect at the same time, the first player resolves them first. 

Some tiles use adjacency. In the above grid, 0 is adjacent to 1 and 3, but not to 4. 

Producing a shape means: add to your storage.

Burning a shape removes it from the game. It doesn't go to the powerups section.

End of round effects happen before end of round bonuses are calculated.

Moving/Placing/Receiving are different i.e. if you receive a shape on a tile it will not trigger on place or on move effects.

When you receive or move a shape, it may not trump.

A **set** is 1 circle, 1 square, and 1 triangle

A **pair** is any 2 shapes

Some tiles can only be used once per round. This applies to everyone, players do not get to each use it once per round