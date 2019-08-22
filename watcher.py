import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import driveClip
from config import Config
import os.path
import json
from multiprocessing import Process
from datetime import datetime
import logging
import sys

class Watcher:
    DIRECTORY_TO_WATCH = os.path.join(Config.BASE_DIR, Config.QUEUE_LOCATION)

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
                logging.debug("Watcher: Sleeping")
                print("Watcher: Sleeping")
        except:
            self.observer.stop()
            logging.error("-1 - Error")
            print("-1 - Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print("Watcher: Event found: {}".format(event.event_type))
        logging.debug("Watcher: Event found: {}".format(event.event_type))
        logging.debug("Directory: {}".format(os.path.basename(event.src_path)))
        if event.is_directory:
            return None

        # Windows is created
        # Linux is modified
        elif event.event_type == 'modified':
            time.sleep(1)
            # Take any action here when a file is first created.
            print("Received event {} for file {} - Beginning render job." .format(event.event_type, event.src_path))
            logging.debug("Received event {} for file {} - Beginning render job." .format(event.event_type, event.src_path))
            # Testing print
            print("File found: {}".format(os.path.relpath(event.src_path, Watcher.DIRECTORY_TO_WATCH)))
            logging.debug("File found: {}".format(os.path.relpath(event.src_path, Watcher.DIRECTORY_TO_WATCH)))
            print("Source path: {}".format(event.src_path))
            logging.debug("Source path: {}".format(event.src_path))

            # Open the file for reading
            json_file = open(event.src_path, 'r')
            json_data = json.load(json_file)
            # If job hasn't been done
            if json_data['status'] == False:
                # Get the ID and run the render on it
                proj_id = json_data["id"]
                print("Project ID is {}".format(proj_id))
                logging.debug("Project ID is {}".format(proj_id))
                try:
                    logging.debug("Starting render serivce...")
                    p = Process(target=driveClip.render_video, args=(proj_id, json_data["compressedRender"], json_data["chunkRender"],))
                    #driveClip.render_video(proj_id, compress_render=json_data["compressedRender"])
                    p.start()
                    p.join()
                except OSError as e:
                    logging.error("Error: {}".format(e))
                    if e.errno == 6:
                        logging.error("Error is safely ignorable, continuing")
                        pass
                    else:
                        return
                except Exception as ex:
                    logging.error("Exception occured:")
                    logging.error(ex)
                    return

                    
                # Update the complete time at the end and dump it to file 
                logging.debug("Updating JSON status file")
                json_data['dateCompleted'] = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
                json_data['status'] = True
                logging.debug("JSON Data for {}:".format(proj_id))
                logging.debug(json_data)
                with open(event.src_path, "w") as json_write:
                    json.dump(json_data, json_write)
                logging.debug("File written.")
                print("File written")
            else:
                logging.debug("File already rendered")
                print("File already rendered")


if __name__ == '__main__':

    log_file_name = os.path.join(
        Config.BASE_DIR,
        Config.LOGS_LOCATION,
        Config.WATCHER_LOGS, 
        datetime.now().strftime("%Y.%m.%d-%H-%M-%S") + "_render_watcher_instance.log"
    )

    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file_name
    )

    logging.debug("Beginning watcher service")

    w = Watcher()
    w.run()