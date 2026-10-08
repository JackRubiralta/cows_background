# cows_background

Turn your [Omarchy](https://omarchy.org) desktop background into cyriak's
[**cows & cows & cows**](https://www.youtube.com/watch?v=FavUpD_IjVY), looping
forever with no title and no credits. One command undoes it and leaves no
trace. It also works with any other video file or URL.

```bash
cows-background on                  # cows, ping-pong (the whole video)
cows-background on --mode perfect   # cows, the 19.5 s section that loops invisibly
cows-background off                 # back to your normal background
```

## Install

```bash
git clone https://github.com/JackRubiralta/cows_background
cd cows_background
./install.sh
```

Needs `mpvpaper`, `ffmpeg`, `yt-dlp`, and `python3` with `python-numpy`
(numpy is only for `perfect` mode on your own videos). Install any missing
ones with `omarchy pkg add <name>`. The first `on` downloads the video and
prepares it, which takes a few minutes. After that it starts instantly.

## Commands

| Command | What it does |
|---|---|
| `cows-background on [video]` | Make the video your background. It stays on after a reboot until you turn it off. |
| `cows-background off` | Put your normal background back. `--purge` also deletes the prepared videos. |
| `cows-background status` | Show what is playing. |
| `cows-background list` | Show the built-in videos, their modes and what is prepared. |
| `cows-background preview [video]` | Watch the loop in a normal window first. |
| `cows-background build [video]` | Prepare a video without turning it on. |

`[video]` is a built-in name (`cows` is the default), a video file or a URL.

| Option | |
|---|---|
| `-m, --mode pingpong` | Play forward, then backward, forever. The picture never jumps. |
| `-m, --mode perfect` | Loop the section of the video where the end matches the start best. |
| `-m, --mode loop` | Play start to end, then start over. |
| `--start SEC`, `--end SEC` | For files and URLs: use only that part of the video. |
| `--min-loop SEC` | Shortest section `perfect` may choose (default 10). |
| `--fit` | Show the whole frame with black bars instead of filling the screen. |

```bash
cows-background on ~/Videos/rain.mp4 --mode perfect --min-loop 5
cows-background on "https://www.youtube.com/watch?v=..." --mode pingpong --start 3 --end 60
```

## How the cows loops were made

The end of cows & cows & cows doesn't match its start. The
loop finder (`lib/find-loop.py`) compared every frame of the video with every
other frame, and no part of the ending matches anything earlier. Any loop of
the whole video forward would have a visible jump. So there are two modes:

- **pingpong** (the default) uses everything between the title (gone by frame
  164) and the fade to black (frame 3176): 2 min forward, then 2 min backward.
  Because it never jumps, there is no seam.
- **perfect** loops 70.48 s to 89.96 s. Frame 2250 is almost identical to
  frame 1762, and the jump between them is smaller than a normal step from
  one frame to the next, so the seam is invisible.

For your own videos, `perfect` runs the same search and tells you how good the
seam it found is.

## No trace

Omarchy draws its wallpaper on Hyprland's *background* layer. This plays the
video with `mpvpaper` on the *bottom* layer, which sits above the wallpaper
and below every window and the bar. Your theme, background, Omarchy shell and
Hyprland config are never touched.

`on` writes one systemd user service, `~/.config/systemd/user/cows-background.service`,
so the video comes back after a reboot. `off` stops it, disables it and
deletes the file. Your desktop is then exactly as it was, and the only thing
left is the prepared video in `~/.cache/cows-background` (`off --purge`
removes that too). `./uninstall.sh` removes the command as well.

On laptops with NVIDIA graphics plus an Intel or AMD chip, the video renders
and decodes on the Intel/AMD chip, so the wallpaper doesn't keep the NVIDIA
GPU awake. mpvpaper also pauses the video while windows hide it completely.

## Credits

*cows & cows & cows* is by [cyriak](https://www.youtube.com/@cyriak) (2010).
This repository does not contain the video. It is downloaded from cyriak's
own upload when you first turn it on.
