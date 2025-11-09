# Convergence Jukebox - Paid Song Bug Debugging

## Bug Description
When users select multiple paid songs in quick succession, only the first song plays correctly. The second and subsequent paid songs are selected, appear in the upcoming display, but never play. The PaidMusicPlayList.txt file ends up empty.

## Root Cause Identified (0.82.8)
**In-memory copy gets out of sync with the file:**
- Engine reads PaidMusicPlayList.txt at loop start: [24]
- Engine plays song 24 (takes 2+ minutes)
- During playback, GUI adds songs to file: [24, 26, 28]
- After playing, engine deletes from OLD in-memory copy (which only had [24])
- Engine writes back an empty or incomplete list, losing songs 26, 28
- Result: Songs added during playback are lost

## Investigation Findings
From 0.82.7 test log:
- 14:21:01 - Engine reads file [24], starts playing
- 14:23:50 - While playing, GUI adds [24, 26, 28] to file
- After play completes - Engine deletes from stale in-memory copy, loses 26 & 28
- File ends up empty because engine had old data in memory

The file was being written correctly by the GUI, but the engine's in-memory copy was outdated.

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

## Solution - Attempt 1 (0.82.6-0.82.7)
File locking and atomic writes were implemented but were treating the wrong problem. The real issue was the engine's in-memory copy being outdated, not file access conflicts.

## Solution - Final Fix (0.82.8)
Re-read the file from disk AFTER playing a song but BEFORE deleting and writing back:
1. Engine reads PaidMusicPlayList.txt: [24]
2. Engine plays song 24
3. **NEW: Engine re-reads file to capture additions: [24, 26, 28]**
4. Engine deletes first song from updated list: [26, 28]
5. Engine writes back: [26, 28]
6. Loop continues, will play song 26 next

Implementation (line 1167 in Engine playback loop):
- Added `self.paid_music_playlist = read_paid_playlist(self.paid_music_playlist_file)` after play_song() completes
- Added safety check: only delete if list is not empty
- This ensures all selections made during playback are preserved

## Modules Modified
- 0.82.8 - Convergence-Jukebox-Full-2026.py (main file with file re-read fix) - COMMITTED TO GITHUB

## Testing Notes
- Select a paid song and let it play for a while (don't skip)
- While it's playing, select 1-2 more songs
- After the first song finishes, verify the next song plays immediately
- Repeat: the second song should play all the way through
- Check log entries to confirm all songs are queued and played
- Verify songs play in the order they were selected (not skipped)
