# Enemy AI

## Pathfinding (BFS)

Enemies use BFS to find paths toward the player or base.

### Common Issues & Fixes

**Problem:** Enemies couldn't find player/base in maze-like levels (Levels 2/3) while working in Level 1.

**Root cause:** 
- BFS checked `len(visited) > max_depth` inside the loop after adding neighbors, causing premature exit
- Fallback checked cells near the target, not the enemy, so rarely found useful directions
- max_depth was too shallow (50) for larger maze layouts

**Fix:**
1. Changed loop condition to `while queue and len(visited) <= max_depth` (cleaner exit)
2. Increased max_depth from 50 → 80 (deeper search for steel mazes)
3. Better fallback: use the last direction found by BFS (even if incomplete) if walkable
4. New fallback: scan all 4 adjacent cells from enemy, pick closest to target by Manhattan distance

**Additional fix (regression):** BFS was only tracking the "first" direction from start, but that direction might not get closer to the target. Changed to track the `best_dir` — the direction that got closest to target during the search.

This ensures enemies always get a direction, even in tight steel mazes.

## Targeting

- Level 1: All enemies chase player
- Level 2+: 50% of enemies target the base (set in `game.py:_spawn_enemies`)
- Base-targeting enemies have 70% chance to path toward base, 30% toward player

## Shooting

- Line-of-fire detection (`_can_hit_pos`) checks if player/base is in current direction
- Shoot cooldown enforced via `shoot_cooldown` counter

## Movement

- Grid-based movement with configurable `ENEMY_MOVE_INTERVAL`
- `ENEMY_DIRECTION_CHANGE_CHANCE` (30%) adds randomness to prevent straight-line spam
- Stuck detection: if position unchanged for 3 moves, try perpendicular directions