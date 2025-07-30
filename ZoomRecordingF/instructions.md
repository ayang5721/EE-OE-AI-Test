# Dependencies
pillow
imagehash
moviepy
webvtt

fpdf (for saving as a PDF)

## How to dowload dependecies
open "terminal" app on your PC

run the following commands: 

pip install moviepy pillow imagehash webvtt-py fpdf

# Instructions

## Setup
Save your zoom recordings in a single folder structured like below:

zoom_meetings/  
├── meeting1/  
│   ├── meeting1.mp4         ← the Zoom video  
│   └── meeting1.vtt         ← the Zoom transcript file  
├── meeting2/  
│   ├── meeting2.mp4  
│   └── meeting2.vtt  

Each meeting folder (meeting1, meetin2, etc) should already be structured correctly if downloaded from Zoom Cloud  
Each meeting folder must have a .vtt and .mp4 file (it can also include other files but they will not be used)

## Running the script


