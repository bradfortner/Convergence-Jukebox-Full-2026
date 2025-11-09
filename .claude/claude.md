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

## Solution Enhanced (0.82.6)
Attempted Windows file locking (msvcrt.locking) to prevent race conditions, but this caused "[Errno 13] Permission denied" errors because the file locking calls were incompatible with text mode file operations.

## Solution Finalized (0.82.7)
Replaced msvcrt.locking with robust retry logic and atomic file operations:
- Added `read_paid_playlist()` with retry logic (5 retries, 10ms delays)
- Added `write_paid_playlist()` with atomic operations (write to temp file, then rename)
- Replaced all four file operations (GUI read/write at lines 2533 & 2556, Engine read/write at lines 1131 & 1169) with these functions

This approach prevents race conditions without triggering permission errors:
- Retry logic handles brief file access conflicts
- Atomic writes ensure complete data or nothing (no partial writes)
- Works seamlessly with text mode file operations
- Cleans up temporary files on error

## Modules Modified
- 0.82.7 - Convergence-Jukebox-Full-2026.py (main file with atomic writes and retries) - COMMITTED TO GITHUB

## Testing Notes
- When selecting multiple songs, watch both the file writes and the playback order
- Check PaidMusicPlayList.txt after selection to confirm all songs are present
- Verify songs play in the order they were selected
- Test with rapid succession selections to verify file locking prevents race conditions
