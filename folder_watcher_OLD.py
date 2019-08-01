import os, time, sys, subprocess


import driveClip
# Change this to correct drive
share_path = "G:/project/queue"
before = dict ([(f, None) for f in os.listdir (share_path)])
while 1:
	# Change this as desired
	time.sleep (3)
	after = dict (
		[(f, None) for f in os.listdir (share_path)]
		)

	added = [f for f in after if not f in before]
	removed = [f for f in before if not f in after]

	if added: 
		print("Added: ", ", ".join (added))

	if removed: 
		print("Removed: ", ", ".join (removed))
		before = after
