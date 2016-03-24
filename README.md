# legacy inspector frontend

### Motivation
The tool serves as a standalone remote inspector frontend of chromium/blink based web runtime for Android. It's only tested on Ubuntu 14.04 now and should work on any unix-like OS.

The tool offers the possibility to develop based on blink-inspector for:
  1. custom interative ui
  2. devlop new debug protocol if you got your own backend in web runtime

Moreover, the tool offers an additional remote targets/webruntime detector.

### Requirements:
  * python2.x
  * adb
  * chrome browser on host. Alternatively, any web socket supported browsers should be fine

### Steps
1. setup env
  *  `make`
2. invoke the tool
  *  `./inspector_ui.py`

THAT'S IT. HAVE FUN AND GOOD LUCK!
