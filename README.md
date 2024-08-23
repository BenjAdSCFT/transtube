# transtube
Download videos from youtube and add subtitles


## Usage

usage: main.py [-h] --link LINK [--origin ORIGIN] [--target TARGET] [-b]

Create a video with subtitles (possibly dual) from a link to a youtube video.

optional arguments:

  -h, --help       show this help message and 
  
  --link LINK      A youtube link in the format https://www.youtube.com/watch?v=00000000000

  --origin ORIGIN  Language of the original video. Default: Russian.

  --target TARGET  Language of the target subtitles. Default: English
  
  -b, --both       Keep both languages in the subtitle.