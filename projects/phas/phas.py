from nicegui import ui, app
from pathlib import Path

import numpy as np

import io
import wave
import base64
import yaml
import re
import time

path = Path(__file__).parent / ""

# Distance between ghost footprints/footsteps, in metres. speed = steps/second * STEP_LENGTH_M.
# This is an approximation (~100 taps/min == 1.7 m/s); tune it if your readings are consistently off.
STEP_LENGTH_M = 1.02
DEFAULT_SPEED_TOLERANCE = 0.15  # m/s, adjustable in the Speed tab

# Ghosts whose two listed speeds are the ends of a continuous range rather than two discrete speeds.
RANGE_SPEED_GHOSTS = {'Deogen'}


# Inline SVG icons, keyed by file stem (no remote images / files needed).
SVG_ICONS = {
    'emf5': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="6.099999mm"
   height="6.0999994mm"
   viewBox="0 0 6.099999 6.0999994"
   version="1.1"
   id="svg1"
   inkscape:export-filename="emf5.svg"
   inkscape:export-xdpi="96"
   inkscape:export-ydpi="96"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <sodipodi:namedview
     id="namedview1"
     pagecolor="#505050"
     bordercolor="#eeeeee"
     borderopacity="1"
     inkscape:showpageshadow="0"
     inkscape:pageopacity="0"
     inkscape:pagecheckerboard="0"
     inkscape:deskcolor="#505050"
     inkscape:document-units="mm">
    <inkscape:page
       x="0"
       y="0"
       width="6.099999"
       height="6.0999994"
       id="page2"
       margin="0"
       bleed="0" />
  </sodipodi:namedview>
  <defs
     id="defs1" />
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-115.46492,-95.64458)">
    <rect
       style="fill:#000000;fill-opacity:1;fill-rule:evenodd;stroke:#00ffcf;stroke-width:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1"
       id="rect17"
       width="6"
       height="6"
       x="115.51492"
       y="95.694572"
       rx="1"
       ry="1" />
    <path
       style="fill:#00ff6f;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 443.75425,383.1503 c -0.0987,-0.0219 -0.23006,-0.0666 -0.29184,-0.0993 -0.20141,-0.10659 -0.44509,-0.36729 -0.54452,-0.58256 l -0.0938,-0.20308 -0.0101,-2.13775 c -0.0109,-2.29155 -0.005,-2.40082 0.15034,-2.68734 0.11718,-0.21647 0.39106,-0.45887 0.6118,-0.54146 0.24431,-0.0914 0.60159,-0.0914 0.8459,0 0.25266,0.0945 0.51134,0.33974 0.64514,0.61152 l 0.10686,0.21706 v 2.26899 2.26898 l -0.101,0.21214 c -0.17229,0.36189 -0.4709,0.59978 -0.85525,0.68133 -0.20523,0.0435 -0.23054,0.0431 -0.46348,-0.009 z"
       id="path12"
       transform="scale(0.26458333)" />
    <path
       style="fill:#00ff6f;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 439.77679,383.16194 c -0.35702,-0.074 -0.66409,-0.31331 -0.8272,-0.64462 l -0.10727,-0.2179 v -0.80099 -0.80099 l 0.10727,-0.21789 c 0.29912,-0.60759 1.00714,-0.83003 1.61495,-0.50737 0.22821,0.12114 0.39417,0.29825 0.50903,0.54321 0.0836,0.17826 0.0863,0.20388 0.0964,0.90985 0.0117,0.81595 -0.0109,0.95687 -0.19778,1.23497 -0.25573,0.3805 -0.75976,0.59205 -1.19541,0.50173 z"
       id="path13"
       transform="scale(0.26458333)" />
    <path
       style="fill:#21ff00;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 443.62579,383.09278 c -0.1729,-0.0547 -0.24545,-0.10202 -0.41021,-0.26742 -0.11032,-0.11074 -0.2401,-0.283 -0.28913,-0.38376 l -0.089,-0.18281 0.01,-2.28131 0.01,-2.2813 0.0775,-0.15601 c 0.12063,-0.24287 0.34106,-0.46547 0.57492,-0.5806 0.18404,-0.0906 0.23951,-0.10217 0.4899,-0.10217 0.2498,0 0.30606,0.0117 0.48787,0.10117 0.24366,0.11995 0.43396,0.31561 0.57099,0.58707 l 0.0998,0.19763 v 2.25493 2.25493 l -0.0872,0.18427 c -0.0977,0.20647 -0.29579,0.43745 -0.46767,0.54526 -0.29679,0.18616 -0.62126,0.22274 -0.97703,0.11012 z"
       id="path14"
       transform="scale(0.26458333)" />
    <path
       style="fill:#c0ff00;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 447.78194,383.16329 c -0.36277,-0.0756 -0.6736,-0.31572 -0.83619,-0.64597 l -0.10727,-0.21789 v -4.29251 -4.29251 l 0.094,-0.20347 c 0.11364,-0.24604 0.33926,-0.46777 0.60061,-0.59026 0.15654,-0.0734 0.23134,-0.0875 0.46404,-0.0875 0.24314,0 0.30363,0.0125 0.48956,0.10145 0.25453,0.12172 0.46096,0.32338 0.5808,0.56739 l 0.0883,0.17973 v 4.32445 4.32446 l -0.11171,0.20602 c -0.25231,0.46535 -0.77959,0.72713 -1.26209,0.62658 z"
       id="path15"
       transform="scale(0.26458333)" />
    <path
       style="fill:#ffb000;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 451.78453,383.16128 c -0.3795,-0.0779 -0.74331,-0.3813 -0.88855,-0.74095 l -0.0757,-0.18756 v -6.23374 -6.23374 l 0.0757,-0.18756 c 0.0426,-0.1054 0.14706,-0.26559 0.23858,-0.36572 0.5188,-0.56766 1.40778,-0.50825 1.8348,0.12261 0.23321,0.34455 0.2171,-0.15047 0.2171,6.66743 0,5.92168 -0.002,6.15043 -0.0614,6.34053 -0.17754,0.57043 -0.77439,0.93494 -1.34055,0.8187 z"
       id="path16"
       transform="scale(0.26458333)" />
    <path
       style="fill:#ff1d00;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.320662;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1"
       d="m 455.77238,383.16232 c -0.2074,-0.0429 -0.5197,-0.22202 -0.64759,-0.37143 -0.0621,-0.0725 -0.15274,-0.21307 -0.2015,-0.31234 l -0.0887,-0.1805 v -8.2899 -8.2899 l 0.0875,-0.18662 c 0.1225,-0.26134 0.34423,-0.48696 0.59027,-0.6006 0.17649,-0.0815 0.24243,-0.094 0.49721,-0.094 0.25849,0 0.31702,0.0114 0.48778,0.0953 0.24713,0.12134 0.45639,0.3306 0.56738,0.56738 l 0.0872,0.18592 0.008,8.28001 0.008,8.28001 -0.0708,0.18939 c -0.096,0.25692 -0.3963,0.55991 -0.64821,0.65403 -0.22046,0.0824 -0.49144,0.11168 -0.67724,0.0733 z"
       id="path17"
       transform="scale(0.26458333)" />
  </g>
</svg>''',
    'dots': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   height="19"
   viewBox="0 -960 760 760"
   width="19"
   fill="#e3e3e3"
   version="1.1"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1" />
  <path
     d="m 6,-486 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 0,-160 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 105.5,334.5 Q 100,-323 100,-340 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 100,-483 100,-500 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 100,-643 100,-660 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 100,-803 100,-820 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 146,334 Q 240,-475 240,-500 q 0,-25 17.5,-42.5 17.5,-17.5 42.5,-17.5 25,0 42.5,17.5 17.5,17.5 17.5,42.5 0,25 -17.5,42.5 -17.5,17.5 -42.5,17.5 -25,0 -42.5,-17.5 z m 0,-160 Q 240,-635 240,-660 q 0,-25 17.5,-42.5 17.5,-17.5 42.5,-17.5 25,0 42.5,17.5 17.5,17.5 17.5,42.5 0,25 -17.5,42.5 -17.5,17.5 -42.5,17.5 -25,0 -42.5,-17.5 z m 14,306 Q 260,-323 260,-340 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-480 Q 260,-803 260,-820 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z M 286,-206 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 0,-720 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 131.5,468.5 Q 400,-475 400,-500 q 0,-25 17.5,-42.5 17.5,-17.5 42.5,-17.5 25,0 42.5,17.5 17.5,17.5 17.5,42.5 0,25 -17.5,42.5 -17.5,17.5 -42.5,17.5 -25,0 -42.5,-17.5 z m 0,-160 Q 400,-635 400,-660 q 0,-25 17.5,-42.5 17.5,-17.5 42.5,-17.5 25,0 42.5,17.5 17.5,17.5 17.5,42.5 0,25 -17.5,42.5 -17.5,17.5 -42.5,17.5 -25,0 -42.5,-17.5 z m 14,306 Q 420,-323 420,-340 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-480 Q 420,-803 420,-820 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z M 446,-206 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 0,-720 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 145.5,614.5 Q 580,-323 580,-340 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 580,-483 580,-500 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 580,-643 580,-660 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z m 0,-160 Q 580,-803 580,-820 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 -11.5,11.5 -28.5,11.5 -17,0 -28.5,-11.5 z M 726,-486 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z m 0,-160 q -6,-6 -6,-14 0,-8 6,-14 6,-6 14,-6 8,0 14,6 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 z"
     id="path1"
     style="fill:#1cff00;fill-opacity:1" />
</svg>''',
    'uv': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   height="19.964285"
   viewBox="0 -960 721.95794 798.57139"
   width="18.048948"
   fill="#e3e3e3"
   version="1.1"
   id="svg1"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1">
    <linearGradient
       id="linearGradient6">
      <stop
         style="stop-color:#7b3bf0;stop-opacity:1;"
         offset="0.14550926"
         id="stop6" />
      <stop
         style="stop-color:#98f270;stop-opacity:1;"
         offset="1"
         id="stop7" />
    </linearGradient>
    <linearGradient
       xlink:href="#linearGradient6"
       id="linearGradient7"
       x1="54.851387"
       y1="-369.42462"
       x2="667.10638"
       y2="-752.00403"
       gradientUnits="userSpaceOnUse"
       gradientTransform="translate(-3.868e-6)" />
  </defs>
  <path
     d="m 359.8,-862 q 106,0 200,45.5 94,45.5 157,131.5 7,9 4.5,16 -2.5,7 -8.5,12 -6,5 -14,4.5 -8,-0.5 -14,-8.5 -55,-78 -141.5,-119.5 -86.5,-41.5 -183.5,-41.5 -97,0 -182,41.5 -85,41.5 -141,119.5 -6,9 -14,10 -8,1 -14,-4 -7,-5 -8.50000001,-12.5 Q -1.2,-675 4.8,-683 q 62,-85 155.5,-132 93.5,-47 199.5,-47 z m 0,94 q 135,0 232,90 97,90 97,223 0,50 -35.5,83.5 -35.5,33.5 -86.5,33.5 -51,0 -87.5,-33.5 -36.5,-33.5 -36.5,-83.5 0,-33 -24.5,-55.5 -24.5,-22.5 -58.5,-22.5 -34,0 -58.5,22.5 -24.5,22.5 -24.5,55.5 0,97 57.5,162 57.5,65 148.5,91 9,3 12,10 3,7 1,15 -2,7 -8,12 -6,5 -15,3 -104,-26 -170,-103.5 -66,-77.5 -66,-189.5 0,-50 36,-84 36,-34 87,-34 51,0 87,34 36,34 36,84 0,33 25,55.5 25,22.5 59,22.5 34,0 58,-22.5 24,-22.5 24,-55.5 0,-116 -85,-195 -85,-79 -203,-79 -118,0 -203,79 -85,79 -85,194 0,24 4.5,60 4.5,36 21.5,84 3,9 -0.5,16 -3.5,7 -11.5,10 -8,3 -15.5,-0.5 -7.5,-3.5 -10.5,-11.5 -15,-39 -21.5,-77.5 -6.5,-38.5 -6.5,-79.5 0,-133 96.5,-223 96.5,-90 230.5,-90 z m 0,-192 q 64,0 125,15.5 61,15.5 118,44.5 9,5 10.5,12 1.5,7 -1.5,14 -3,7 -10,11 -7,4 -17,-1 -53,-27 -109.5,-41.5 -56.5,-14.5 -115.5,-14.5 -58,0 -114,13.5 -56,13.5 -107,42.5 -8,5 -16,2.5 -8,-2.5 -12,-10.5 -4,-8 -2,-14.5 2,-6.5 10,-11.5 56,-30 117,-46 61,-16 124,-16 z m 0,289 q 93,0 160,62.5 67,62.5 67,153.5 0,9 -5.5,14.5 -5.5,5.5 -14.5,5.5 -8,0 -14,-5.5 -6,-5.5 -6,-14.5 0,-75 -55.5,-125.5 -55.5,-50.5 -131.5,-50.5 -76,0 -130.5,50.5 -54.5,50.5 -54.5,125.5 0,81 28,137.5 28,56.5 82,113.5 6,6 6,14 0,8 -6,14 -6,6 -14,6 -8,0 -14,-6 -59,-62 -90.5,-126.5 -31.5,-64.5 -31.5,-152.5 0,-91 66,-153.5 66,-62.5 159,-62.5 z m -1,196 q 9,0 14.5,6 5.5,6 5.5,14 0,75 54,123 54,48 126,48 6,0 17,-1 11,-1 23,-3 9,-2 15.5,2.5 6.5,4.5 8.5,13.5 2,8 -3,14 -5,6 -13,8 -18,5 -31.5,5.5 -13.5,0.5 -16.5,0.5 -89,0 -154.5,-60 -65.5,-60 -65.5,-151 0,-8 5.5,-14 5.5,-6 14.5,-6 z"
     id="path1"
     style="mix-blend-mode:difference;fill:url(#linearGradient7);fill-rule:evenodd;stroke:none;stroke-width:393;stroke-dasharray:none" />
</svg>''',
    'freezing': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   height="20"
   viewBox="0 -960 760 800"
   width="19"
   fill="#e3e3e3"
   version="1.1"
   id="svg1"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1">
    <linearGradient
       id="linearGradient1">
      <stop
         style="stop-color:#c9fff8;stop-opacity:1;"
         offset="0.18523437"
         id="stop1" />
      <stop
         style="stop-color:#00f5da;stop-opacity:1;"
         offset="0.7844705"
         id="stop2" />
    </linearGradient>
    <linearGradient
       xlink:href="#linearGradient1"
       id="linearGradient2"
       x1="702.25824"
       y1="-761.36926"
       x2="57.741787"
       y2="-358.63068"
       gradientUnits="userSpaceOnUse" />
  </defs>
  <path
     d="m 720,-640 q -17,0 -28.5,-11.5 Q 680,-663 680,-680 q 0,-17 11.5,-28.5 11.5,-11.5 28.5,-11.5 17,0 28.5,11.5 11.5,11.5 11.5,28.5 0,17 -11.5,28.5 Q 737,-640 720,-640 Z m -400,480 v -144 l -104,104 -56,-56 160,-160 v -64 H 256 L 96,-320 40,-376 144,-480 H 0 v -80 h 144 l -104,-104 56,-56 160,160 h 64 v -64 l -160,-160 56,-56 104,104 v -144 h 80 v 144 l 104,-104 56,56 -160,160 v 64 h 320 v 80 H 576 l 104,104 -56,56 -160,-160 h -64 v 64 l 160,160 -56,56 -104,-104 v 144 z m 360,-600 v -200 h 80 v 200 z"
     id="path1"
     style="fill:url(#linearGradient2);fill-opacity:1;stroke-width:4022.48;stroke-dasharray:none" />
</svg>''',
    'orbs': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="17.658449mm"
   height="19.121237mm"
   viewBox="0 0 17.658449 19.121237"
   version="1.1"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1" />
  <g
     id="layer1"
     transform="translate(-3.688419,-2.903831)">
    <circle
       style="fill:#d8eb76;fill-opacity:1;stroke:none;stroke-width:10;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1"
       id="path10"
       cx="15.738834"
       cy="4.653831"
       r="1.75" />
    <circle
       style="fill:#d8eb76;fill-opacity:1;stroke:none;stroke-width:10;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1"
       id="path11"
       cx="6.6884193"
       cy="9.635066"
       r="3" />
    <circle
       style="fill:#d8eb76;fill-opacity:1;stroke:none;stroke-width:10;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1"
       id="path12"
       cx="16.34687"
       cy="17.025068"
       r="5" />
  </g>
</svg>''',
    'writing': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->

<svg
   fill="#000000"
   height="799.99994"
   width="799.99994"
   version="1.1"
   id="Layer_1"
   viewBox="0 0 512.00096 512.00096"
   xml:space="preserve"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"><defs
   id="defs4" />
<g
   id="g2">
	<g
   id="g1">
		<path
   d="m 435.2,51.201 v -25.6 c 0,-14.14 -11.46,-25.6 -25.6,-25.6 H 51.2 c -14.14,0 -25.6,11.46 -25.6,25.6 v 38.4 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 25.6 H 12.8 c -7.074,0 -12.8,5.726 -12.8,12.8 0,7.074 5.726,12.8 12.8,12.8 h 12.8 v 38.4 c 0,14.14 11.46,25.6 25.6,25.6 h 358.4 c 14.14,0 25.6,-11.46 25.6,-25.6 V 238.797 l -25.6,25.6 V 486.4 H 51.2 V 448 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 396.8 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 345.6 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 C 76.8,325.726 71.074,320 64,320 H 51.2 V 294.4 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 243.2 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 192 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 140.8 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 0,-7.074 -5.726,-12.8 -12.8,-12.8 H 51.2 V 89.6 H 64 c 7.074,0 12.8,-5.726 12.8,-12.8 C 76.8,69.726 71.074,64 64,64 H 51.2 V 25.6 h 358.4 v 25.6 h 25.6 z"
   id="path1"
   style="fill:#e35050;fill-opacity:1" />
	</g>
</g>
<g
   id="g4">
	<g
   id="g3">
		<path
   d="m 504.499,97.101 -25.6,-25.6 C 473.907,66.5 467.353,64 460.8,64 c -6.554,0 -13.107,2.5 -18.099,7.501 L 437.393,76.8 H 384 c -3.396,0 -6.647,1.348 -9.054,3.746 l -76.8,76.8 18.099,18.099 73.054,-73.045 h 22.494 L 212.301,301.901 c -1.946,1.946 -3.567,4.19 -4.796,6.656 l -25.6,51.2 c -4.932,9.856 -2.995,21.76 4.796,29.551 4.915,4.915 11.469,7.501 18.108,7.501 3.883,0 7.799,-0.887 11.443,-2.705 l 51.2,-25.6 c 2.458,-1.229 4.71,-2.85 6.656,-4.796 l 230.4,-230.4 c 9.992,-10.001 9.992,-26.214 -0.009,-36.207 z m -299.699,274.1 19.567,-39.134 19.567,19.558 z m 60.254,-34.654 -25.6,-25.6 221.346,-221.346 25.6,25.6 z"
   id="path2"
   style="fill:#ffffff;fill-opacity:1" />
	</g>
</g>
</svg>''',
    'spirit': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   height="20"
   viewBox="0 -960 760 800"
   width="19"
   fill="#e3e3e3"
   version="1.1"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1" />
  <path
     d="m 195,-515 q -35,-35 -35,-85 v -240 q 0,-50 35,-85 35,-35 85,-35 50,0 85,35 35,35 35,85 v 240 q 0,50 -35,85 -35,35 -85,35 -50,0 -85,-35 z m 113.5,-56.5 Q 320,-583 320,-600 v -240 q 0,-17 -11.5,-28.5 Q 297,-880 280,-880 q -17,0 -28.5,11.5 Q 240,-857 240,-840 v 240 q 0,17 11.5,28.5 11.5,11.5 28.5,11.5 17,0 28.5,-11.5 z M 320,-200 H 240 V -323 Q 136,-337 68,-416 0,-495 0,-600 h 80 q 0,83 58.5,141.5 58.5,58.5 141.5,58.5 11,0 20.5,-1 9.5,-1 19.5,-3 z m 240,-40 q 8,0 14,-6 6,-6 6,-14 0,-8 -6,-14 -6,-6 -14,-6 -8,0 -14,6 -6,6 -6,14 0,8 6,14 6,6 14,6 z m -20,-80 h 40 V -480 H 540 Z M 418.5,-218.5 Q 360,-277 360,-360 360,-443 418.5,-501.5 477,-560 560,-560 q 83,0 141.5,58.5 58.5,58.5 58.5,141.5 0,83 -58.5,141.5 Q 643,-160 560,-160 q -83,0 -141.5,-58.5 z M 280,-720 Z"
     id="path1"
     style="fill:#ffb300;fill-opacity:1" />
</svg>''',
    'brain': r'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->

<svg
   height="592.20471"
   width="800"
   version="1.1"
   id="_x32_"
   viewBox="0 0 512 379.01102"
   xml:space="preserve"
   sodipodi:docname="brain.svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"><defs
   id="defs1"><linearGradient
     id="linearGradient1"
     inkscape:collect="always"><stop
       style="stop-color:#ffe1e1;stop-opacity:0.50757575;"
       offset="0"
       id="stop1" /><stop
       style="stop-color:#d76049;stop-opacity:1;"
       offset="1"
       id="stop2" /></linearGradient><linearGradient
     inkscape:collect="always"
     xlink:href="#linearGradient1"
     id="linearGradient2"
     x1="57.050644"
     y1="94.892456"
     x2="454.9494"
     y2="417.10452"
     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview
   id="namedview1"
   pagecolor="#505050"
   bordercolor="#eeeeee"
   borderopacity="1"
   inkscape:showpageshadow="0"
   inkscape:pageopacity="0"
   inkscape:pagecheckerboard="0"
   inkscape:deskcolor="#505050"><inkscape:page
     x="0"
     y="0"
     width="512"
     height="379.01102"
     id="page2"
     margin="0"
     bleed="0" /></sodipodi:namedview>
<style
   type="text/css"
   id="style1">
	.st0{fill:#000000;}
</style>
<g
   id="g1"
   transform="translate(0,-66.492995)">
	<path
   class="st0"
   d="m 497.879,222.264 -0.131,-0.122 0.106,0.106 c -2.291,-2.332 -4.86,-4.443 -7.69,-6.324 -0.974,-0.008 -1.956,-0.204 -2.896,-0.613 -1.521,-0.647 -2.708,-1.735 -3.518,-3.036 -4.524,-2.151 -9.261,-3.534 -14.063,-4.213 -4.197,-0.58 -7.093,-4.45 -6.504,-8.639 0.58,-4.181 4.451,-7.093 8.623,-6.513 4.786,0.68 9.54,1.907 14.146,3.682 0.728,-3.338 1.137,-6.741 1.137,-10.194 -0.008,-7.527 -1.775,-15.136 -5.547,-22.278 v -0.008 c -4.311,-8.181 -10.594,-14.554 -17.99,-18.931 -6.472,-3.829 -13.769,-6.096 -21.28,-6.595 -0.548,6.807 -2.176,13.639 -5.023,20.233 -1.669,3.878 -6.168,5.677 -10.055,4.008 -3.878,-1.669 -5.677,-6.168 -4.008,-10.055 2.724,-6.348 4.008,-12.91 4.025,-19.397 0,-0.933 -0.041,-1.857 -0.082,-2.782 -0.507,-8.982 -3.502,-17.679 -8.574,-25.067 -5.081,-7.396 -12.19,-13.467 -21.05,-17.278 -6.348,-2.741 -12.926,-4.026 -19.406,-4.026 -12.411,0 -24.437,4.778 -33.503,13.212 1.702,5.776 2.643,11.879 2.643,18.195 0,4.221 -3.428,7.641 -7.65,7.641 -4.23,0 -7.658,-3.42 -7.658,-7.641 0,-6.201 -1.141,-12.076 -3.22,-17.54 l 0.004,0.007 c -3.526,-9.228 -9.773,-17.14 -17.753,-22.735 -7.977,-5.596 -17.634,-8.868 -28.135,-8.868 -9.138,0 -17.639,2.47 -24.948,6.79 -5.846,3.452 -10.898,8.108 -14.858,13.589 7.743,10.628 12.313,23.75 12.309,37.887 0,4.222 -3.424,7.641 -7.65,7.641 -4.234,0 -7.658,-3.42 -7.658,-7.641 -0.004,-12.436 -4.578,-23.742 -12.169,-32.382 l -0.012,-0.008 c -9.028,-10.292 -22.2,-16.738 -36.946,-16.747 -10.247,0.008 -19.696,3.109 -27.571,8.452 -7.862,5.342 -14.108,12.91 -17.81,21.786 -2.402,5.801 -3.751,12.199 -3.751,18.899 0,4.222 -3.42,7.641 -7.65,7.641 -4.226,0 -7.653,-3.42 -7.653,-7.641 0,-6.21 0.904,-12.223 2.54,-17.917 -5.764,-2.34 -11.994,-3.617 -18.408,-3.617 -3.628,0 -7.318,0.417 -11.012,1.26 -10.893,2.504 -20.036,8.394 -26.687,16.338 -4.806,5.735 -8.251,12.542 -10.051,19.872 15.827,0.295 31.633,6.398 43.819,18.334 3.018,2.953 3.072,7.796 0.114,10.815 -2.953,3.018 -7.8,3.068 -10.82,0.122 -9.576,-9.367 -21.95,-14.022 -34.369,-14.038 -2.225,0 -4.443,0.164 -6.644,0.45 l -0.028,0.008 h -0.012 -0.008 c -10.428,1.424 -20.453,6.169 -28.422,14.284 -9.372,9.58 -14.015,21.926 -14.018,34.353 0,7.126 1.542,14.26 4.618,20.838 2.426,5.187 5.796,10.03 10.132,14.284 l 0.008,0.008 c 4.93,4.843 10.607,8.402 16.657,10.75 3.939,1.513 5.898,5.948 4.372,9.891 -1.526,3.943 -5.956,5.907 -9.895,4.377 -7.928,-3.06 -15.41,-7.764 -21.86,-14.096 -2.827,-2.782 -5.355,-5.76 -7.572,-8.893 C 3.13,250.465 0,260.373 0,270.452 c 0.004,7.813 1.866,15.708 5.817,23.112 4.442,8.296 10.872,14.759 18.424,19.185 5.984,3.51 12.664,5.694 19.541,6.463 l -0.013,-0.442 c 0,-4.05 0.377,-8.026 1.088,-11.871 0.769,-4.156 4.762,-6.897 8.914,-6.137 4.16,0.762 6.905,4.77 6.14,8.926 -0.548,2.945 -0.839,5.98 -0.839,9.081 0,1.178 0.045,2.356 0.127,3.534 0.09,1.252 0.221,2.446 0.41,3.584 l 0.008,0.057 0.008,0.057 c 3.502,24.028 24.245,41.954 48.547,41.954 1.162,0 2.34,-0.05 3.523,-0.132 h 0.012 c 10.775,-0.777 20.449,-4.941 28.107,-11.404 5.408,-4.565 9.801,-10.251 12.832,-16.666 1.804,-3.82 6.369,-5.456 10.19,-3.648 3.82,1.808 5.452,6.365 3.648,10.186 -3.261,6.897 -7.723,13.114 -13.11,18.432 3.01,9.229 8.659,17.189 16.023,23.088 8.463,6.766 19.106,10.742 30.593,10.742 1.162,0 2.331,-0.033 3.526,-0.123 h 0.012 c 7.289,-0.531 14.031,-2.61 20.007,-5.874 -0.941,-4.41 -1.461,-8.918 -1.461,-13.466 0,-9.392 2.074,-18.948 6.419,-27.948 1.832,-3.82 6.41,-5.408 10.214,-3.574 3.804,1.832 5.408,6.405 3.571,10.21 -3.33,6.922 -4.901,14.161 -4.901,21.312 0,5.015 0.778,9.988 2.27,14.734 l 0.004,0.008 c 3.919,12.501 12.779,23.398 25.533,29.542 6.893,3.329 14.133,4.9 21.288,4.9 11.339,0 22.441,-3.968 31.215,-11.167 l 0.028,-0.016 c 5.339,-4.401 9.83,-9.965 13.037,-16.608 l 0.008,-0.025 c 3.002,-6.21 4.565,-12.722 4.851,-19.218 0.188,-4.221 3.763,-7.494 7.993,-7.314 4.213,0.197 7.485,3.764 7.305,7.986 -0.384,8.508 -2.438,17.098 -6.373,25.214 l 0.008,-0.008 c -3.166,6.561 -7.306,12.345 -12.166,17.27 9.024,12.975 24.037,21.124 40.268,21.116 3.018,0 6.079,-0.287 9.171,-0.859 11.806,-2.234 21.77,-8.468 28.855,-17.083 7.078,-8.614 11.192,-19.562 11.192,-31.122 0,-0.36 -0.008,-0.711 -0.017,-1.047 v -0.048 c -0.041,-2.618 -0.319,-5.334 -0.843,-8.067 -1.219,-6.504 -3.705,-12.403 -7.1,-17.639 -4.942,-4.36 -10.456,-10.038 -15.634,-16.37 -5.506,-6.749 -10.611,-14.12 -14.031,-21.557 -2.25,-4.982 -3.854,-9.998 -3.886,-15.307 0,-2.348 0.352,-4.778 1.211,-7.126 0.867,-2.348 2.274,-4.606 4.14,-6.455 v 0.008 c 2.986,-2.994 7.829,-2.994 10.816,0 2.986,2.978 2.986,7.838 0,10.815 -0.295,0.311 -0.442,0.54 -0.589,0.925 -0.147,0.393 -0.27,0.974 -0.27,1.832 -0.033,1.922 0.762,5.196 2.496,8.934 1.71,3.739 4.254,7.936 7.241,12.084 5.931,8.312 13.629,16.477 19.422,21.435 l 0.786,0.679 0.581,0.85 c 4.745,7.06 8.197,15.184 9.866,24.061 v 0.008 c 0.238,1.268 0.393,2.527 0.556,3.804 0.753,0.033 1.522,0.098 2.291,0.098 9.711,-0.008 19.471,-2.879 28.062,-8.918 6.831,-4.794 12.026,-10.97 15.552,-17.9 3.526,-6.938 5.359,-14.62 5.351,-22.35 0,-7.241 -1.62,-14.497 -4.892,-21.263 -3.003,0.974 -6.062,1.743 -9.18,2.282 -4.164,0.721 -8.124,-2.078 -8.852,-6.25 -0.704,-4.164 2.094,-8.115 6.258,-8.835 13.557,-2.34 25.951,-10.226 33.642,-22.899 4.859,-7.977 7.15,-16.755 7.159,-25.452 0,-12.745 -4.966,-25.246 -14.121,-34.508 z M 147.188,163.851 c 7.322,-8.64 17.033,-14.784 27.464,-18.801 10.452,-4.017 21.68,-5.956 32.439,-5.956 10.476,0.008 20.522,1.816 29.076,5.743 3.833,1.768 5.51,6.316 3.742,10.154 -1.775,3.844 -6.323,5.514 -10.16,3.746 -5.919,-2.757 -13.99,-4.352 -22.658,-4.344 -8.901,0 -18.416,1.652 -26.937,4.941 -8.537,3.272 -16.023,8.173 -21.287,14.399 v 0.008 c -2.724,3.215 -7.555,3.625 -10.783,0.892 -3.224,-2.732 -3.628,-7.559 -0.896,-10.782 z m 174.198,180.952 c -8.893,0.016 -16.971,-0.99 -24.347,-2.7 0.204,2.103 0.343,4.434 0.343,6.93 0,4.998 -0.532,10.7 -2.114,16.69 -1.579,5.98 -4.226,12.263 -8.403,18.301 -2.405,3.469 -7.17,4.336 -10.652,1.931 -3.472,-2.405 -4.34,-7.167 -1.93,-10.652 3.068,-4.434 4.999,-9.008 6.188,-13.49 1.186,-4.484 1.608,-8.868 1.608,-12.779 0.004,-5.392 -0.806,-9.867 -1.391,-12.387 -3.734,-1.693 -7.207,-3.607 -10.414,-5.702 -12.808,-8.312 -21.382,-19.258 -26.777,-29.69 -3.604,-6.962 -5.822,-13.72 -6.987,-19.578 -0.671,-3.338 -1.002,-6.39 -1.002,-9.146 0,-4.23 3.423,-7.657 7.657,-7.657 4.226,0 7.65,3.427 7.65,7.657 -0.013,2.242 0.466,5.956 1.681,10.178 1.206,4.246 3.133,9.081 5.919,13.94 5.584,9.736 14.46,19.504 28.139,25.845 9.142,4.238 20.518,6.995 34.832,7.003 4.226,0 7.654,3.428 7.654,7.649 0,4.229 -3.428,7.657 -7.654,7.657 z m 53.882,-55.886 c -1.579,3.919 -6.03,5.833 -9.957,4.254 -3.91,-1.562 -5.816,-5.988 -4.271,-9.916 v -0.008 l 0.05,-0.114 c 0.048,-0.132 0.122,-0.36 0.228,-0.671 0.205,-0.606 0.491,-1.571 0.778,-2.766 0.589,-2.414 1.17,-5.825 1.17,-9.572 l -0.025,-0.548 c -10.48,3.567 -20.248,5.195 -29.235,5.195 -13.581,0.017 -25.321,-3.706 -34.885,-9.359 -9.58,-5.653 -17.025,-13.139 -22.588,-20.723 -6.324,-8.631 -14.628,-16.355 -24.13,-21.836 -9.515,-5.482 -20.167,-8.737 -31.482,-8.745 -9.932,0.024 -20.457,2.495 -31.473,8.525 -10.435,5.743 -17.172,13.384 -21.513,21.762 -4.315,8.37 -6.119,17.549 -6.115,25.886 -0.021,7.731 1.6,14.718 3.726,19.144 1.808,3.829 0.176,8.386 -3.645,10.202 -3.816,1.8 -8.382,0.18 -10.194,-3.648 -3.313,-7.06 -5.171,-15.929 -5.191,-25.697 0.004,-9.695 1.935,-20.281 6.644,-30.418 -9.487,2.152 -18.302,3.109 -26.348,3.1 -4.34,0.008 -8.426,-0.294 -12.321,-0.769 -0.27,1.014 -0.74,1.996 -1.448,2.856 l -0.004,0.007 h -0.008 l -0.09,0.115 c -0.082,0.115 -0.225,0.295 -0.413,0.532 -0.373,0.491 -0.929,1.252 -1.628,2.242 -1.391,1.971 -3.325,4.9 -5.416,8.59 -4.189,7.364 -8.946,17.729 -11.274,29.387 -0.822,4.148 -4.859,6.84 -9.003,6.005 -4.144,-0.827 -6.831,-4.852 -6.001,-9.008 2.774,-13.843 8.222,-25.582 12.963,-33.936 2.466,-4.345 4.732,-7.756 6.39,-10.096 -6.242,-1.873 -11.646,-4.164 -16.051,-6.496 -10.072,-5.351 -15.336,-10.726 -15.762,-11.159 -2.933,-3.044 -2.842,-7.886 0.197,-10.815 3.035,-2.929 7.862,-2.839 10.79,0.172 l 0.008,-0.008 0.074,0.074 0.471,0.45 c 0.45,0.409 1.182,1.039 2.18,1.825 1.996,1.578 5.081,3.746 9.204,5.923 8.258,4.369 20.604,8.795 37.142,8.812 11.61,0 25.33,-2.218 41.25,-8.337 4.041,-3.755 8.68,-7.192 14.03,-10.112 13.086,-7.191 26.295,-10.415 38.828,-10.406 14.293,0 27.612,4.148 39.127,10.791 11.527,6.659 21.308,15.79 28.826,26.032 4.561,6.218 10.578,12.214 18.015,16.592 7.457,4.377 16.305,7.232 27.116,7.241 7.392,0 15.753,-1.366 25.186,-4.68 -2.282,-3.714 -5.727,-7.29 -11.38,-10.513 -3.681,-2.078 -4.974,-6.758 -2.896,-10.431 2.079,-3.682 6.75,-4.975 10.424,-2.904 9.056,5.105 15.119,11.862 18.628,18.915 3.543,7.052 4.606,14.194 4.606,20.273 -0.032,10.599 -3.108,18.241 -3.304,18.789 z m -2.864,-93.765 c -17.884,0.008 -33.527,-4.819 -46.183,-12.125 -1.771,2.487 -4.168,5.58 -7.249,8.975 -6.921,7.592 -17.106,16.518 -30.724,21.41 -3.98,1.424 -8.357,-0.654 -9.781,-4.638 -1.419,-3.984 0.654,-8.354 4.634,-9.777 10.035,-3.559 18.436,-10.611 24.27,-16.984 2.688,-2.912 4.79,-5.645 6.316,-7.772 -7.567,-6.381 -13.52,-13.646 -17.594,-21.107 -3.895,-7.183 -6.144,-14.563 -6.165,-21.762 0,-4.221 3.424,-7.641 7.649,-7.641 4.226,0 7.654,3.42 7.654,7.641 -0.02,3.87 1.338,9.032 4.299,14.44 2.949,5.424 7.428,11.085 13.262,16.141 11.682,10.128 28.577,17.892 49.611,17.892 4.222,0 7.65,3.428 7.65,7.657 10e-4,4.231 -3.427,7.65 -7.649,7.65 z m 60.328,107.763 c -2.699,3.256 -7.526,3.714 -10.783,1.023 -3.255,-2.692 -3.714,-7.519 -1.022,-10.775 8.328,-10.144 11.42,-20.338 11.446,-30.115 0.016,-8.893 -2.692,-17.491 -6.963,-24.715 -4.246,-7.241 -10.07,-13.016 -15.682,-16.232 -3.739,-2.168 -7.298,-3.158 -10.113,-3.15 -4.23,0 -7.657,-3.42 -7.657,-7.65 0,-4.221 3.428,-7.649 7.657,-7.649 4.664,0 9.212,1.138 13.532,3.043 4.311,1.898 8.402,4.574 12.198,7.846 7.568,6.545 14.006,15.47 18.039,25.918 2.692,6.963 4.304,14.604 4.304,22.588 0.024,13.14 -4.459,27.195 -14.956,39.868 z"
   id="path1"
   style="fill:url(#linearGradient2);fill-opacity:1" />
</g>
</svg>''',
}


def svg_data_uri(name: str) -> str:
    """Return a data: URI for an icon in SVG_ICONS (accepts 'emf5' or 'emf5.svg'), usable as an image source."""
    svg = SVG_ICONS[Path(name).stem]
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('ascii')



def sanity_thresholds(sanity) -> list[float]:
    """Flatten a ghost's 'Sanity' entry (float, list of floats, or list of {label: float}) to floats."""
    if not isinstance(sanity, list):
        sanity = [sanity]
    out = []
    for item in sanity:
        if isinstance(item, dict):
            item = list(item.values())[0]
        if isinstance(item, (int, float)):
            out.append(float(item))
    return out


def passes_sanity(sanity, selected_pct: float) -> bool:
    """
    Inclusive sanity filter. A ghost stays only if it can still hunt above the selected sanity (%),
    i.e. at least one hunt threshold is strictly greater than it. Selecting 50 therefore removes every
    ghost whose threshold is 50% (or lower). A threshold of 100%+ means "any sanity" and always stays.
    Ghosts with no numeric threshold (e.g. 'Any') are never hidden.
    """
    thresholds = sanity_thresholds(sanity)
    if not thresholds:
        return True
    return any(t >= 1 or round(t * 100, 6) > selected_pct for t in thresholds)


def load_from_yaml():
    """
    Parse seven.yaml to extract:
      - MOVE_LIST: ordered list of move names (series > data > name)
      - MOVE_COLORS: {name: hex color} (series > data > itemStyle > color)
      - WIN_MAP: {name: [names it beats]} (series > links, source beats target)
    Falls back to sensible defaults if the file isn't found.
    """
    yaml_path = Path(f'{path}/phas.yaml')
    if yaml_path.exists():
        data = yaml.safe_load(yaml_path.read_text())
        return data
    else:
        return 'Broken'


def folder_card(
        title: str,
        *,
        bg: str = '#252A41',
        border: str = '#70B77E',
        width: int = 400,
        height: int = 200,
        tab_width: int = 155,
        tab_height: int = 30,
        radius: int = 14,
        curve: int = 60,
        border_width: float = 0,
        title_color: str | None = None,
        padding: int = 16,
) -> ui.column:
    title_color = title_color or border

    path = (
        f'M {radius},0 '
        f'H {tab_width} '
        f'C {tab_width + curve * 0.6},0 {tab_width + curve * 0.4},{tab_height} {tab_width + curve},{tab_height} '
        f'H {width - radius} '
        f'Q {width},{tab_height} {width},{tab_height + radius} '
        f'V {height - radius} '
        f'Q {width},{height} {width - radius},{height} '
        f'H {radius} '
        f'Q 0,{height} 0,{height - radius} '
        f'V {radius} '
        f'Q 0,0 {radius},0 '
        f'Z'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="position:absolute;inset:0;display:block;overflow:visible;">'
        f'<path d="{path}" fill="{bg}" stroke="{border}" stroke-width="{border_width}"/>'
        f'</svg>'
    )

    wrapper = ui.element('div').style(
        f'position:relative; width:{width}px; height:{height}px;'
    ).classes('flex')
    with wrapper:
        svg_holder = ui.html(svg).classes('folder-svg').style('position:absolute; inset:0; pointer-events:none;')

        with ui.element('div').style(
                f'position:absolute; top:0; left:0; width:{tab_width}px; height:{tab_height}px; '
                f'display:flex; align-items:center; padding-left:{padding}px; z-index:1; '
                f'box-sizing:border-box;'
        ):
            ui.label(title).style(
                f'color:{title_color}; font-family: "Trade Winds", system-ui; font-weight:600; font-size:24px; '
                f'white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'
            )

        content = ui.column().style(
            f'position:absolute; top:{tab_height}px; left:0; right:0; bottom:0; '
            f'padding:{padding}px; z-index:1; overflow:auto; gap:8px; '
            f'box-sizing:border-box;'
        ).classes('flex')

    content.svg_holder = svg_holder  # lets callers toggle the highlight border without a re-render
    return content


# noinspection bad-index
def page():
    app.add_static_files('/static', Path(f'{path}/static'))

    # Variables

    ev_keys = {
        'EMF 5': 'emf5.svg',
        'D.O.T.S. Projector': 'dots.svg',
        'Ultraviolet': 'uv.svg',
        'Freezing Temperatures': 'freezing.svg',
        'Ghost Orbs': 'orbs.svg',
        'Ghost Writing': 'writing.svg',
        'Spirit Box': 'spirit.svg',
    }

    game_data = load_from_yaml()

    evidence_markers = {}

    for ev in game_data['Evidence']:
        smart = game_data['Evidence'][ev]
        evidence_markers[ev] = {
            'icon': svg_data_uri(smart['img']),
            'state': None,
            'color': '#FFF'
        }

    ghost_folders = {}
    ghost_tests = {}
    for ghost in game_data['Ghosts']:
        ghost_tests[ghost] = []

    for ghost in game_data['Ghosts']:
        sg = game_data['Ghosts'][ghost]

        evidence_imgs = []
        for i in sg['Evidence']:
            evidence_imgs.append(svg_data_uri(ev_keys[i]))

        for test in game_data['Tests']:

            test_gp = game_data['Tests'][test]  # eg. Equipment
            for sub_test in test_gp:
                sub_test_gp = test_gp[sub_test]  # eg. Incense
                if sub_test_gp.get(ghost):
                    ghost_tests[ghost].append({'type': test, 'name': sub_test, 'text': sub_test_gp.get(ghost)})

        speed_table_vals = game_data.get('GhostSpeedTables', {}).get(sg.get('SpeedTable'))
        if speed_table_vals:
            speed_vals = [v for k, v in speed_table_vals.items() if k != 'Metrics']
        elif isinstance(sg['Speed'], list):
            speed_vals = list(sg['Speed'])
        else:
            speed_vals = []  # e.g. Mimic: 'Any'
        speed_vals = [float(v) for v in speed_vals if isinstance(v, (int, float))]

        ghost_folders[ghost] = {
            'name': ghost,
            'evidence': sg['Evidence'],
            'ev_imgs': evidence_imgs,
            'sanity': sg['Sanity'],
            'sanity_img': svg_data_uri('brain'),
            'speed': sg['Speed'],
            'speed_tt': sg.get('SpeedTooltip'),
            'speed_t': sg.get('SpeedTable'),
            'ghost_tests': ghost_tests[ghost],
            'speed_vals': speed_vals,
        }

    # State

    crossed = set()  # (test_type, sub_test, ghost) entries the user has crossed out
    ev_rows = {}  # key -> row in the Evidence Tests panel (built once)
    folder_rows = {}  # key -> row inside a ghost folder (rebuilt with the folders)
    folder_svgs = {}  # ghost -> folder svg holder
    folder_match = {}  # ghost -> whether its border is currently highlighted
    ev_groups = []  # (container element, [keys]) for sub-test blocks and test-type cards
    taps = []  # monotonic timestamps of the current speed test window
    suspend = {'evidence': False}

    # Functions

    def is_complete(ghost):
        tests = ghost_folders[ghost]['ghost_tests']
        return bool(tests) and all((t['type'], t['name'], ghost) in crossed for t in tests)

    def set_crossed(row, is_crossed):
        if is_crossed:
            row.classes(add='test-crossed')
        else:
            row.classes(remove='test-crossed')

    def toggle_test(key):
        ghost = key[2]
        was_complete = is_complete(ghost)
        crossed.symmetric_difference_update({key})
        is_crossed = key in crossed
        for row in (ev_rows.get(key), folder_rows.get(key)):
            if row is not None:
                set_crossed(row, is_crossed)
        if is_complete(ghost) != was_complete:
            handle_evidence()  # reorder folders / recolor the name

    def current_speed():
        if len(taps) < 2 or taps[-1] <= taps[0]:
            return None
        return STEP_LENGTH_M * (len(taps) - 1) / (taps[-1] - taps[0])

    def speed_matches(ghost, speed, tol):
        vals = ghost_folders[ghost]['speed_vals']
        if not vals:
            return False
        if ghost in RANGE_SPEED_GHOSTS and len(vals) >= 2:
            return min(vals) - tol <= speed <= max(vals) + tol
        return any(abs(v - speed) <= tol for v in vals)

    def update_speed_matches():
        speed = current_speed()
        tol = tolerance.value if tolerance.value is not None else DEFAULT_SPEED_TOLERANCE
        for ghost, holder in folder_svgs.items():
            match = speed is not None and speed_matches(ghost, speed, tol)
            if folder_match.get(ghost) != match:
                folder_match[ghost] = match
                if match:
                    holder.classes(add='folder-match')
                else:
                    holder.classes(remove='folder-match')

    def refresh_speed():
        speed = current_speed()
        speed_lbl.set_text(f'{speed:.2f} m/s' if speed is not None else ' _._ m/s')
        tap_lbl.set_text(f'Taps: {len(taps)}')
        update_speed_matches()

    def tap_speed():
        taps.append(time.monotonic())
        refresh_speed()

    def new_test():
        taps.clear()
        refresh_speed()

    def reset_all():
        suspend['evidence'] = True
        for marker in evidence_markers.values():
            marker['state'].set_value('N')
        sanity_select.set_value(0)  # back to "no sanity filter"
        suspend['evidence'] = False
        crossed.clear()
        for row in ev_rows.values():
            set_crossed(row, False)
        taps.clear()
        speed_lbl.set_text(' _._ m/s')
        tap_lbl.set_text('Taps: 0')
        handle_evidence()

    def on_evidence_change():
        if not suspend['evidence']:
            handle_evidence()

    def on_key(e):
        if not e.action.keydown or e.action.repeat:
            return
        if e.modifiers.ctrl or e.modifiers.alt or e.modifiers.meta:
            return
        key = (e.key.name or '').lower()
        if key == 'f':
            tap_speed()
        elif key == 'n':
            new_test()
        elif key == 'r':
            reset_all()

    def update_ev_visibility(active):
        """Show Evidence Tests only for ghosts still possible; hide emptied blocks/cards."""
        for key, row in ev_rows.items():
            row.set_visibility(key[2] in active)
        for container, keys in ev_groups:
            container.set_visibility(any(k[2] in active for k in keys))

    def build_ev_tests():
        with ev_tests:
            with ui.row().classes('justify-center'):
                for test_type in game_data['Tests']:
                    type_keys = []
                    type_card = ui.card().classes('w-full lg:w-120 rounded-lg bg-slate-800/50')
                    ev_groups.append((type_card, type_keys))
                    with type_card:
                        ui.label(test_type).classes('ghost text-xl')
                        ui.separator()
                        for sub_test in game_data['Tests'][test_type]:
                            sub_keys = []
                            sub_block = ui.element('div').classes('border-l-2 px-2 rounded-r-lg bg-slate-200/10')
                            ev_groups.append((sub_block, sub_keys))
                            with sub_block:
                                ui.label(sub_test).classes('ghost text-lg')
                                for ghost_test, text in game_data['Tests'][test_type][sub_test].items():
                                    key = (test_type, sub_test, ghost_test)
                                    row = ui.row().classes('text-sm my-2 cursor-pointer test-item')
                                    row.on('click', lambda _, k=key: toggle_test(k))
                                    with row:
                                        ui.label(ghost_test).classes('iceberg text-sm text-gray-200 w-36')
                                        ui.label(text).classes('overlock text-sm text-gray-400 w-64')
                                    ev_rows[key] = row
                                    sub_keys.append(key)
                                    type_keys.append(key)

    def handle_evidence():
        folders.clear()
        folder_rows.clear()
        folder_svgs.clear()
        folder_match.clear()

        active = {}
        gathered = {}
        tested = {}
        val_map = {'N': None, 'T': True, 'F': False}

        for evi in evidence_markers:
            se = evidence_markers[evi]
            gathered[evi] = val_map[se['state'].value]

        # Determine which ghosts are still active based on gathered evidence
        for ghost in ghost_folders:
            data = ghost_folders[ghost]
            ghost_evidence = data['evidence']

            if not passes_sanity(data['sanity'], sanity_select.value - 5 or 0):
                continue  # no hunt threshold above the selected sanity

            mapped = [gathered[e] for e in ghost_evidence]

            if False in mapped:
                continue  # a required piece of evidence was ruled out

            non_none = [v for v in mapped if v is not None]
            if non_none and not all(v is True for v in non_none):
                continue  # some evidence is neither confirmed True nor still unknown

            # exclude if any evidence NOT in this ghost's list has been confirmed True
            outside_true = any(
                gathered[e] is True
                for e in gathered
                if e not in ghost_evidence
            )
            if outside_true:
                continue

            active[ghost] = data

        with folders:
            ordered = sorted(active.items(), key=lambda kv: is_complete(kv[0]))  # stable: finished ghosts last
            for ghost, data in ordered:
                with folder_card(ghost, title_color='#EF4444' if is_complete(ghost) else None) as fcard:
                    folder_svgs[ghost] = fcard.svg_holder
                    with ui.row().classes('w-full h-full'):
                        with ui.column().classes('w-36 p-0'):  # Left side of folder
                            with ui.row():  # Evidence
                                for i in range(len(data['evidence'])):
                                    with ui.image(data['ev_imgs'][i]).classes('w-5 object-contain') as ev_icon:
                                        ev_icon.tooltip(data['evidence'][i])
                            with ui.scroll_area().classes(
                                    'w-full h-24 justify-center bg-indigo-950 rounded-sm border-2 border-indigo-800 gap-0'):  # Sanity thresholds

                                if type(data['sanity']) is float:
                                    with ui.row().classes('w-full'):
                                        ui.image(data['sanity_img']).classes('w-7 p-1')
                                        c_classes = 'ghost text-lg'
                                        if data['sanity'] > 0.65:
                                            c_classes += ' text-red-600'
                                        elif data['sanity'] < 0.5:
                                            c_classes += ' text-lime-400'
                                        ui.label(f'{round(data['sanity'] * 100)}%').classes(c_classes)

                                elif type(data['sanity']) is list:
                                    if type(data['sanity'][0]) is dict:
                                        opt_key = {
                                            'Still': 0,
                                            'Walking': 1,
                                            'Weakened': 2,
                                            'Normal': 3,
                                            'Enraged': 4,
                                            'Movement': 5,
                                            'Light Switch On': 6,
                                            'Light Switch Off': 7,
                                            'Calm': 8,
                                            'Aggressive': 9,
                                            'Near Firelights': 10,
                                            'Ability': 11,
                                            'Active Equipment': 12,
                                            'Old': 13,
                                            'Young': 14,
                                            'Talking': 15,
                                            'Copies mimicked ghost': 16
                                        }

                                        for sanity in data['sanity']:
                                            sk, si = list(sanity.keys())[0], list(sanity.values())[0]

                                            with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                                c_classes = 'ghost text-lg'
                                                if si > 0.65:
                                                    c_classes += ' text-red-600'
                                                elif si < 0.5:
                                                    c_classes += ' text-lime-400'

                                                ui.image(data['sanity_img']).classes('w-7 p-0 m-x-0 -m-y-4')
                                                ui.label(f'{round(si * 100)}%').classes(c_classes)
                                    else:
                                        for si in data['sanity']:
                                            with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                                c_classes = 'ghost text-lg p-0 m-y-0 m-x-2'
                                                if si > 0.65:
                                                    c_classes += ' text-red-600'
                                                elif si < 0.5:
                                                    c_classes += ' text-lime-400'

                                                ui.image(data['sanity_img']).classes('w-7 p-0 -m-x-3 -m-y-4')
                                                ui.label(f'{round(si * 100)}%').classes(c_classes)

                                else:

                                    opt_key = {
                                        'Still': 0,
                                        'Walking': 1,
                                        'Weakened': 2,
                                        'Normal': 3,
                                        'Enraged': 4,
                                        'Movement': 5,
                                        'Light Switch On': 6,
                                        'Light Switch Off': 7,
                                        'Calm': 8,
                                        'Aggressive': 9,
                                        'Near Firelights': 10,
                                        'Ability': 11,
                                        'Active Equipment': 12,
                                        'Old': 13,
                                        'Young': 14,
                                        'Talking': 15,
                                        'Copies mimicked ghost': 16
                                    }

                                    for sanity in data['sanity']:
                                        sk, si = list(sanity.keys())[0], list(sanity.values())[0]

                                        with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                            c_classes = 'ghost text-lg'
                                            if si > 0.65:
                                                c_classes += ' text-red-600'
                                            elif si < 0.5:
                                                c_classes += ' text-lime-400'

                                            ui.image(data['sanity_img']).classes('w-7 p-0 m-x-0 -m-y-4')
                                            ui.label(f'{round(si * 100)}%').classes(c_classes)

                        with ui.column().classes('w-48 p-0'):
                            speed_card = ui.card() \
                                .classes(
                                'relative w-full h-8 p-0 m-0 bg-cyan-100/10 rounded-md border-2 border-cyan-200') \
                                .props('')
                            with speed_card:
                                if data['speed_tt']:
                                    ui.icon('search').classes('absolute top-0 right-0')
                                if data['speed_t']:
                                    ui.icon('table_view').classes('absolute bottom-0 right-0')
                                speeds = data['speed']
                                with ui.row().classes('w-full'):
                                    ui.icon('directions_run').classes('absolute left-2 top-1').props(
                                        'size=sm color=cyan-4')
                                    if type(speeds) is list and len(speeds) > 1:
                                        speed_label = ui.label(
                                            f'{min(speeds)} - {max(speeds)}'
                                        )
                                    elif type(speeds) is list and len(speeds) == 1:
                                        speed_label = ui.label(speeds)
                                    else:
                                        speed_label = ui.label(
                                            'Unknown Speed'
                                        )

                                speed_label.classes(
                                    'absolute ghost text-lg top-1 left-10 text-cyan-500 text-bold'
                                )

                                if data['speed_tt']:
                                    with speed_card:
                                        ui.tooltip(
                                            data['speed_tt']
                                        ) \
                                            .classes(
                                            'text-lg w-128 bg-grey-950'
                                        ) \
                                            .props(
                                            'anchor="bottom middle" self="bottom middle'
                                        )

                            if data['speed_t'] in game_data[
                                'GhostSpeedTables']:  # Thaye names a table that doesn't exist
                                # data['speed_t'] is the table's name; the rows live in GhostSpeedTables
                                speed_table = game_data['GhostSpeedTables'][data['speed_t']]
                                metric = speed_table.get('Metrics', '')

                                def build_rows(temp='c', speed_table=speed_table, metric=metric):
                                    rows = []
                                    for k, v in speed_table.items():
                                        if k == 'Metrics':  # not a data row; used as the column header
                                            continue
                                        k = str(k)
                                        if metric == 'Temperature':  # '>15', '12-15', '<0'
                                            def convert(m):
                                                if m.isdigit():
                                                    m = int(m)
                                                    return str(round(m * 9 / 5 + 32, 1)) + '°' if temp == 'f' else str(
                                                        m) + '°'
                                                return f' {m} '

                                            label = ''.join(convert(x) for x in re.findall(r'\d+|\D', k))
                                        elif metric == 'Sanity':  # '.45-1' -> '45% - 100%'
                                            label = ' - '.join(f'{round(float(p) * 100)}%' for p in k.split('-'))
                                        else:  # Items
                                            label = k
                                        rows.append({'metric': label, 'speed': v})
                                    return rows

                                with ui.dialog() as speed_dialog, ui.card().classes('w-80 max-h-[80vh]'):
                                    ui.label(f'{ghost} Speed').classes('ghost text-xl text-cyan-500')

                                    speed_tbl = ui.table(
                                        columns=[
                                            {'name': 'metric', 'label': metric, 'field': 'metric', 'align': 'left'},
                                            {'name': 'speed', 'label': 'Speed (m/s)', 'field': 'speed',
                                             'align': 'right'},
                                        ],
                                        rows=build_rows(),
                                    ).props('flat bordered virtual-scroll dense').classes('w-full max-h-[55vh]')

                                    if metric == 'Temperature':
                                        ui.toggle(
                                            {'c': '°C', 'f': '°F'},
                                            value='c',
                                            # bind this ghost's table and row builder; the loop would otherwise
                                            # leave them pointing at the last ghost
                                            on_change=lambda e, tbl=speed_tbl, rows_fn=build_rows: tbl.update_rows(
                                                rows_fn(temp=e.value)
                                            ),
                                        )

                                    ui.button('Close', on_click=speed_dialog.close).props('flat')

                                speed_card.classes('cursor-pointer').on('click', speed_dialog.open)

                            test_card = ui.card() \
                                .classes(
                                'relative w-full h-24 p-0 m-0 bg-yellow-100/10 rounded-md border-2 border-yellow-200') \
                                .props('')

                            with test_card:
                                with ui.scroll_area().classes('w-full h-full'):
                                    if not data['ghost_tests']:
                                        ui.label('No tests right now!').classes('text-bold iceberg')
                                    for test in data['ghost_tests']:
                                        key = (test['type'], test['name'], ghost)
                                        row = ui.element('div').classes(
                                            'rounded-lg text-sm p-0 m-0 cursor-pointer test-item')
                                        row.on('click', lambda _, k=key: toggle_test(k))
                                        with row:
                                            ui.label(test['name']).classes('iceberg')
                                            ui.label(test['text']).classes('overlock')
                                        set_crossed(row, key in crossed)
                                        folder_rows[key] = row

        update_ev_visibility(active)
        update_speed_matches()

    ui.colors(
        primary='#335A33',
        secondary='#E5E7F0',
        accent='#70B77E',
        dark_page='#3C4468',
        positive='#60D336 ',
        negative='#F50031',
        warning='#F0F600'
    )

    ui.add_head_html('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Trade+Winds&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Iceberg&family=Overlock:ital,wght@0,400;0,700;0,900;1,400;1,700;1,900&display=swap" rel="stylesheet">


        <style>.ghost {
            font-family: 'Trade Winds', system-ui;
            font-style: bold;
        }
        .iceberg {
            font-family: "Iceberg", sans-serif;
        }
        .overlock {
            font-family: "Overlock", sans-serif;
        }
        .test-item:hover { background: rgba(255, 255, 255, 0.06); }
        .test-crossed { opacity: 0.35; }
        .test-crossed, .test-crossed * { text-decoration: line-through; }
        .folder-match path { stroke: #FFFFFF !important; stroke-width: 4px !important; }
        </style>
        ''')

    with ui.header():

        ui.button('Evidence', on_click=lambda: evidence_drawer.toggle(), icon='rule').props(
            'color=amber-7 flat rounded dense').classes('ghost !text-md')
        ui.space()
        ui.label('Phasmobobia QRH').classes('ghost text-2xl')

    with ui.left_drawer(elevated=True, fixed=True, top_corner=True, value=True) as evidence_drawer:

        ui.label('Evidence').classes('ghost text-xl')

        for ev in evidence_markers:
            cd = ui.checkbox(on_change=lambda: on_evidence_change(), value='N').props(
                'color=pink dense toggle-indeterminate toggle-order=ft true-value=T false-value=N indeterminate-value=F modal-value=N')
            with cd:
                with ui.row().classes('w-full'):
                    ui.image(evidence_markers[ev]['icon']).classes('w-4 object-contain')
                    ui.label(ev).classes(f'color-{evidence_markers[ev]['color']}')
            evidence_markers[ev]['state'] = cd

        ui.separator()

        ui.label('Map').classes('ghost text-xl')
        map1 = ui.select(list(game_data['Maps']), on_change=lambda e: map_update(e)).classes(
            'ghost w-full !text-sm').props('outlined dense')
        map2 = ui.select([], on_change=lambda: update_map_img()).props('outlined dense').classes('w-full').disable()

        with ui.dialog() as map_dialog, ui.card().classes('w-full md:scale-150 lg:scale-200'):
            dialog_map_img = ui.image().classes('w-full')

        with ui.row().classes('w-full'):

            with ui.column():
                map_info_classes = 'w-full rounded-md border -my-1 py-1 px-1'
                with ui.row().classes(map_info_classes) as map_info_box:
                    ui.label('Size:').classes('text-inherit')
                    ui.space()
                    map_size = ui.label('??')
                with ui.row().classes(map_info_classes):
                    ui.label('Rooms:')
                    ui.space()
                    room_count = ui.label('??')
                with ui.row().classes(map_info_classes):
                    ui.label('Floors:')
                    ui.space()
                    floor_count = ui.label('??')
            with ui.button('', on_click=lambda: open_map_dialog()).classes('grow').props('flat dense'):
                map_img = ui.image().classes('size-20 object-cover')
                ui.icon('link').classes('absolute top-1 right-1').props('color=positive')

        ui.separator()

        with ui.tabs().classes('w-full ghost') as tabs:
            metronome = ui.tab('Speed')
            sanity = ui.tab('Sanity')
        with ui.tab_panels(tabs, value=metronome).classes('w-full'):

            with ui.tab_panel(metronome):
                speed_btn = ui.button(on_click=tap_speed).classes('ghost w-full h-16 p-0 text-xl')

                with speed_btn:
                    with ui.column().classes('p-0 m-0'):
                        ui.label('Speed (F):').classes('text-inherit p-0')
                        speed_lbl = ui.label(' _._ m/s').classes('text-sm p-0')

                tap_lbl = ui.label('Taps: 0').classes('text-xs text-gray-400')

                tolerance = ui.number(
                    'Tolerance (m/s)', value=DEFAULT_SPEED_TOLERANCE, min=0.01, max=1, step=0.05, format='%.2f',
                    on_change=lambda: update_speed_matches(),
                ).classes('w-full').props('outlined dense')

                with ui.button_group().classes('w-full'):
                    ui.button('New (N)', on_click=new_test).classes('grow').props('color=accent')
                    ui.button('Reset (R)', on_click=reset_all).props('color=negative')

            with ui.tab_panel(sanity):
                sanity_select = ui.select(
                    options=[i for i in range(0, 105, 5)],
                    value=0,
                    label="Highest Hunt Sanity",
                    on_change=lambda: on_evidence_change(),  # respects the reset suspend flag
                ) \
                    .classes('w-full justify-center') \
                    .props('rounded outlined color=pink-3')

        def open_map_dialog():
            dialog_map_img.set_source(map_img.source)
            map_dialog.open()

        def update_map_img():

            # noinspection bad-argument-type
            def update_info(map, map2: int | None = None, map2r: bool = False):

                map2_check = type(map2) is int

                map_key = {
                    'Small': ['SM', 'green-500'],
                    'Medium': ['MD', 'yellow-500'],
                    'Large': ['LG', 'rose-500'],
                    '??': ['??', 'slate-500']
                }

                # One : {'size': 'Small', 'Rooms': 12, 'Floors': 2, 'Exits': 1, 'map': 'tanglewood.png'}
                # Two (m) : {'size': 'Medium', 'Rooms': [12, 12, 13, 13], 'Floors': [1, 1, 2, 2], 'Exits': [2, 2, 1, 1], 'map': ['brownstone_restricted_f1_left.png', 'brownstone_restricted_f1_right.png', 'brownstone_restricted_f2_left.png', 'brownstone_restricted_f2_right.png'], 'optional': ['F1 Left', 'F1 Right', 'F2 Left', 'F2 Right']}

                if map2_check is False and not map2r:
                    mc = map_key[map['size']][1]
                    ms = map_key[map['size']][0]
                    rc = map['Rooms']
                    fc = map['Floors']
                elif map2_check is False and map2r:
                    mc = map_key['??'][1]
                    ms = map_key['??'][0]
                    rc = '??'
                    fc = '??'
                elif type(map2) is int:
                    mc = map_key[map['size']][1]
                    ms = map_key[map['size']][0]
                    rc = map['Rooms'][map2]
                    fc = map['Floors'][map2]
                else:
                    mc, ms, rc, fc = None, None, None, None

                    ui.notify('Maps Not Defined!!!! HELP!!!!', type='negative')

                if None not in [mc, ms, rc, fc]:
                    map_size.set_text(ms)
                    room_count.set_text(rc)
                    floor_count.set_text(fc)
                    map_info_box.classes(
                        replace=f'row nowrap w-full rounded-md border -my-1 py-1 px-1 text-{mc} border-{mc}')

            img_source = 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/maps/'
            map_selection = game_data['Maps'][map1.value]
            a = map1.value
            b = map2.value

            if map_selection.get('optional') is None and b is None:
                # map_index = map_selection['optional'].index(b)
                print(f'Map has one option, attempting: {map_selection['map']}')
                update_info(map_selection)
                map_img.set_source(f'{img_source}{map_selection['map']}?ref_type=heads')
            elif map_selection.get('optional') is not None and b is not None:
                map_index = map_selection['optional'].index(b)
                ui.notify(f'Optional Selected: [{map_index}]')
                update_info(map_selection, map_index)
                map_img.set_source(f'{img_source}{map_selection['map'][map_index]}?ref_type=heads')
                print(f'Map and Map2 are set, attempting: {map_selection['map'][map_index]}')
            else:
                print(f'Multiple Maps, awaiting Map2 ... [Options]: {map2.options}')
                update_info(map2, map2r=True)
                map_img.set_source(
                    'https://gitlab.com/xplus-studios/xplus-toolkit/-/raw/main/logo/Icon-maintenence.png?ref_type=heads')

        def map_update(e):
            if game_data['Maps'][e.value].get('optional') is not None:
                map2.enable()
                map2.set_options(game_data['Maps'][e.value].get('optional'))
            else:
                map2.set_options([], value='')
                map2.disable()
            ui.update()
            update_map_img()

    with ui.expansion('Evidence Tests').classes('w-full ghost text-xl justify-center bg-slate-600 rounded-lg'):
        ev_tests = ui.column().classes('justify-center')

    with ui.element('div').classes('grow'):
        folders = ui.row().classes('justify-center')

    build_ev_tests()
    handle_evidence()
    ui.keyboard(on_key=on_key, repeating=False, ignore=['input', 'textarea'])