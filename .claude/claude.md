# Convergence Jukebox - Paid Song Bug Debugging

## Bug Description
When users select multiple paid songs in quick succession, only the first song plays correctly. The second and subsequent paid songs are selected, appear in the upcoming display, but never play. The PaidMusicPlayList.txt file ends up empty.

## Root Cause Identified
**Race condition between GUI and Engine file writes:**
- GUI reads PaidMusicPlayList.txt, appends new song, queues write via background thread
- Engine continuously reloads PaidMusicPlayList.txt each loop iteration
- When engine finishes playing a song and deletes it from the file, it overwrites what the background thread was trying to write
- Result: Only the first song survives in the file; subsequent songs get overwritten

## Investigation Findings
From 0.82.4 logs:
- First song queued [24] → written [24] → played ✓
- Second song queued [24, 26] → written [24, 26] → but file ends up empty
- Third song queued [24, 26, 40] → written [24, 26, 40] → but file ends up empty

The background thread WAS successfully writing the data, but the engine was simultaneously reading and writing its own version, causing the newer songs to be lost.

## Code Flow
**GUI Selection (lines 2500-2549):**
1. Read PaidMusicPlayList.txt
2. Append selected song
3. Queue write to background thread (OLD) / Write directly (NEW in 0.82.5)

**Engine Playback (lines 1125-1180):**
1. Loop: Read PaidMusicPlayList.txt
2. Play first song
3. Delete from in-memory copy
4. Write updated file back
5. Loop back to step 1

## Solution Implemented (0.82.5)
Removed background thread queue. GUI now writes PaidMusicPlayList.txt immediately instead of queuing to async thread. This eliminates the window where the engine can overwrite queued writes.

## Next Steps
1. Test 0.82.5 with multiple paid song selections
2. Verify PaidMusicPlayList.txt contains all songs
3. Verify all songs play in correct order
4. If successful, can remove background thread entirely or repurpose it

## Modules Modified
- 0.82.5 - Convergence-Jukebox-Full-2026.py (main file)

## Testing Notes
- When selecting multiple songs, watch both the file writes and the playback order
- Check PaidMusicPlayList.txt after selection to confirm all songs are present
- Verify songs play in the order they were selected
