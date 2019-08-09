import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import driveClip
from config import Config
import os.path
import json
from multiprocessing import Process
from datetime import datetime

class Watcher:
    DIRECTORY_TO_WATCH = os.path.join(Config.DIR_LOCATION, Config.QUEUE_FOLDER)

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
                print("Watcher: Sleeping")
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print("Watcher: Event found: {}".format(event.event_type))
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            time.sleep(1)
            # Take any action here when a file is first created.
            print("Received event {} for file {} - Beginning render job." .format(event.event_type, event.src_path))
            # Testing print
            print("File found: {}".format(os.path.relpath(event.src_path, Watcher.DIRECTORY_TO_WATCH)))
            print("Source path: {}".format(event.src_path))
            # Open the file for reading
            json_file = open(event.src_path, 'r')
            json_data = json.load(json_file)
            print(json_data['status'])
            # If job hasn't been done
            if json_data['status'] == False:
                # Get the ID and run the render on it
                proj_id = json_data["id"]
                print("Project ID is {}".format(proj_id))
                """                
                p = Process(target=driveClip.render_video, args=(proj_id,))        
                p.start()
                p.join()
                """
                try:
                    driveClip.render_video(proj_id)
                except OSError as e:
                    if e.errno == 6:
                        pass
                # Update the complete time at the end and dump it to file 
                print("Updating JSON status file")
                json_data['dateCompleted'] = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
                json_data['status'] = True
                print(json_data)
                with open(event.src_path, "w") as json_write:
                    json.dump(json_data, json_write)
                print("File written")
            else:
                print("File already rendered")


if __name__ == '__main__':
    w = Watcher()
    w.run()