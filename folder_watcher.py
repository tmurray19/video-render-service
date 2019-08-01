import os, time, sys, subprocess

"""
import driveClip
share_path = "G:/project/queue"
before = dict ([(f, None) for f in os.listdir (share_path)])
while 1:
	time.sleep (1)
	after = dict ([(f, None) for f in os.listdir (share_path)])
	added = [f for f in after if not f in before]
	removed = [f for f in before if not f in after]
	if added: 
		print("Added: ", ", ".join (added))
		print(added[0])
		if added.endswith('.json'):
			driveClip.render_video(added)
	if removed: 
		print("Removed: ", ", ".join (removed))
		before = after
"""

subprocess.Popen([sys.executable, "driveClip.py"])