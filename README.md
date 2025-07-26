{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Gesture Control Media System\
\
An interactive gesture-control Python project using OpenCV and MediaPipe for real-time hand gesture recognition to control volume, brightness, Spotify, and camera photo capture\'97with a live UI panel.\
\
## Features\
\
- **Volume and Brightness Control:** Adjust using 1 or 2 fingers on left/right hand.\
- **Spotify Integration:** Open or play/pause Spotify with simple gestures.\
- **Photo Capture:** Take a picture with a visible 3\'962\'961 countdown.\
- **Robust Calibration:** Ensures left/right assignment is accurate for all users/environments.\
- **Live UI Overlay:** See finger counts, last command, and all gesture mappings on screen.\
\
## Gesture Commands\
\
| Gesture        | Hand   | Fingers | Action                 |\
|----------------|--------|---------|------------------------|\
| Volume Down    | Left   | 1       | Decrease Volume        |\
| Volume Up      | Right  | 1       | Increase Volume        |\
| Brightness Down| Left   | 2       | Decrease Brightness    |\
| Brightness Up  | Right  | 2       | Increase Brightness    |\
| Open Spotify   | Either | 3       | Launch Spotify App     |\
| Play/Pause     | Either | 4       | Toggle Play/Pause      |\
| Click Photo    | Either | 5       | Take Photo (3-2-1)     |\
\
## Installation\
\
1. **Clone the repo and enter the directory:**\
    ```\
    git clone https://github.com/YOURUSERNAME/gesture-media-control.git\
    cd gesture-media-control\
    ```\
\
2. **Install dependencies (Python 3.7+):**\
    ```\
    pip install -r requirements.txt\
    ```\
\
## Usage\
\
}