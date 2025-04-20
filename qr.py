import os
import qrcode

img = qrcode.make("https://shahslovetravel.blogspot.com/p/ai-agents.html")
img.save ("LSAI.png", "PNG")
