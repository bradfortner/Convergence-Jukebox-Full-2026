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

---

# Convergence Jukebox - Rotating Record Popup Timing Bug

## Bug Description (0.82.98)
The rotating record popup appears much sooner than the expected 20 seconds of idle time. While initial testing showed it sometimes waited the full 20 seconds, subsequent tests showed it would appear after only 10-12 seconds on average.

## Root Cause Identified
**Idle timer is only reset by certain keypress events:**
- Line 1622 in main file checks: `if event.startswith('--') and ('KEY' in event or 'PRESSED' in event or event == '--ESC--')`
- This only catches special formatted events like `--ESC--`, arrow keys, etc.
- **Most frequently used keys bypass this check and DON'T reset the idle timer**

## Complete Keymap

### Main Interface Keys (DO NOT reset idle timer)
| Key | Action |
|-----|--------|
| **x** | Add credit (quarter) |
| **T** | Open title search |
| **A** | Open artist search |
| **a** | Select song category A |
| **b** | Select song category B |
| **c** | Select song category C |
| **1-7** | Select song number 1-7 |
| **S** | Complete song selection |

### Main Interface Keys (DO reset idle timer)
| Key | Action |
|-----|--------|
| **Escape** | Exit program |
| **Right Arrow** | Move selection right |
| **Left Arrow** | Move selection left |

### Search Window Keys (All reset idle timer)
| Key | Action |
|-----|--------|
| **Right Arrow** | Next result |
| **Left Arrow** | Previous result |
| **S** | Confirm selection |
| **C** | Delete character |
| **Escape** | Exit search |
| **A-Z, 0-9** | Type search |

### 45RPM Popup Window Keys
| Key | Action | Resets Timer? |
|-----|--------|---------------|
| **x** | Add credit | ❌ No |
| **Escape** | Close popup | ✅ Yes |

## The Problem
When user presses **x** (add credit), **a/b/c** (select category), or **1-7** (select song number), the 20-second idle timer is NOT reset.

**Example sequence from test log:**
- 10:53:29 - X pressed (add credit) → timer NOT reset
- 10:53:39 - Popup appears (only 10 seconds later, not 20)

## Solution
Modify line 1622 to reset `last_keypress_time` for ALL keypress events, not just special formatted ones. This ensures:
- Timer resets consistently whenever user interacts with jukebox
- Popup waits full 20 seconds of actual idle time
- Expected behavior matches observed behavior

## Code Changes Needed
Line 1620-1624: Expand the keypress detection condition to catch simple character events (x, a, b, c, 1-7, S, T, A)

## Modules Modified
- popup_rotating_record_code_module.py - Added logging (0.82.98)
- 0.82.98 - Convergence-Jukebox-Full-2026.py - Added logging calls for popup show/close events

---

# Convergence Jukebox - Pygame/Tkinter Z-Order Limitation

## Issue Description (v0.83.52-59)
Attempted to display a pygame rotating record popup window on top of FreeSimpleGUI (Tkinter-based) windows. Despite extensive debugging across 8 versions, the pygame window could not be made visible above topmost Tkinter windows.

## Root Cause - Fundamental Framework Incompatibility
**Pygame and Tkinter/FreeSimpleGUI use incompatible window management systems:**
- FreeSimpleGUI wraps Tkinter, which uses native OS window handles
- Pygame creates its own SDL-based window system
- Windows OS treats these as fundamentally different window types
- Z-order manipulation APIs (SetWindowPos, SetWindowLong, etc.) fail when trying to make pygame windows appear above topmost Tkinter windows

## What Was Attempted (v0.83.52-59)

### v0.83.52
- Initial attempt: SetWindowPos with HWND_TOPMOST flag
- Result: FAILED - Error code 0 (general failure)

### v0.83.53
- Added comprehensive debug logging
- Result: Confirmed all conditions met, but window invisible

### v0.83.54
- Split SetWindowPos into two separate calls (position first, then topmost)
- Result: FAILED - Error code 1400 (ERROR_INVALID_WINDOW_HANDLE)

### v0.83.55
- Single SetWindowPos call with all parameters
- Added fallback using SetWindowLong + MoveWindow
- Result: FAILED - Window created but invisible

### v0.83.56
- Hide ALL FreeSimpleGUI windows during popup
- Result: SUCCESS - Popup visible on black screen (but background disappeared)

### v0.83.57
- 5-step aggressive Windows API sequence:
  1. SetWindowLong with WS_EX_TOPMOST | WS_EX_LAYERED
  2. MoveWindow to position
  3. ShowWindow with SW_SHOW
  4. SetForegroundWindow + BringWindowToTop
  5. SetWindowPos final enforcement
- Result: FAILED - All steps succeeded but window still invisible

### v0.83.58
- Temporarily disable HWND_TOPMOST on FreeSimpleGUI windows using SetWindowPos(HWND_NOTOPMOST)
- Allow pygame window to appear, then restore topmost
- Result: FAILED - Pygame window still invisible behind Tkinter windows

### v0.83.59
- Accepted reality and reverted to v0.83.56 approach (hide all windows)
- Result: SUCCESS - Only working solution

## Conclusion - Architectural Limitation

**FACT: Pygame windows CANNOT appear above topmost Tkinter/FreeSimpleGUI windows.**

This is not a bug - it's a fundamental architectural limitation of mixing these two GUI frameworks. After exhaustive testing with every available Windows API combination:
- SetWindowPos (all flag variations)
- SetWindowLong with extended styles
- MoveWindow
- ShowWindow
- SetForegroundWindow
- BringWindowToTop
- Disabling topmost on competing windows

**None of these approaches work when pygame and Tkinter windows coexist.**

## Working Solution

The ONLY working solution is to hide all Tkinter windows when showing pygame content:
1. Hide all FreeSimpleGUI windows
2. Show pygame window (appears on black screen)
3. When pygame closes, restore all FreeSimpleGUI windows

This is implemented in v0.83.56 and v0.83.59.

## Recommendation for Future Development

**DO NOT attempt to overlay pygame windows on top of FreeSimpleGUI/Tkinter windows.**

If overlay functionality is required, choose ONE framework:
- **Option 1:** Pure pygame for entire GUI (no Tkinter/FreeSimpleGUI)
- **Option 2:** Pure Tkinter/FreeSimpleGUI (no pygame)
- **Option 3:** Alternative framework like Kivy that handles all rendering internally

Mixing pygame and Tkinter for overlapping UI elements will always fail due to incompatible window management systems.

## Version History
- v0.83.51 - Last stable version before popup experiments
- v0.83.52-59 - Failed attempts to fix z-order (all approaches documented above)
- v0.83.60 - Rollback to v0.83.51 baseline for clean slate
