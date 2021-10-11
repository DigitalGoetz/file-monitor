
import os
import os.path
import subprocess
import time
import threading
from file_sender import FileSender


class DirectoryMonitor:

    def __init__(self, directory) -> None:
        self.watch_dir = directory
        self.sender = FileSender()
        self.filepath_list = []
        self.run_threads = True
        self.watchers = []

        for file in os.listdir(self.watch_dir):
            filepath = self.watch_dir + "/" + file
            
            if os.path.isfile(filepath):
                self.filepath_list.append(filepath)

    def _get_directory_listing(self):
        listing = []
        for file in os.listdir(self.watch_dir):
            filepath = self.watch_dir + "/" + file
            if os.path.isfile(filepath):
                listing.append(filepath)
        return listing

    def _prune_filepath_list(self):
        dir_list = self._get_directory_listing()
        new_filepath_list = []
        for filepath in self.filepath_list:
            if filepath in dir_list:
                new_filepath_list.append(filepath)
            else:
                print("pruning: " + filepath)
        self.filepath_list = new_filepath_list

    def start_monitor(self):
        while True:
            self._prune_filepath_list()
            for filepath in self._get_directory_listing():
                    if filepath not in self.filepath_list:
                        self.filepath_list.append(filepath)
                        watcher = threading.Thread(target=self.start_file_watcher, args=(filepath,))
                        self.watchers.append(watcher)
                        watcher.start()
            time.sleep(1)

    def stop(self):
        self.run_threads = False
        for watcher in self.watchers:
            watcher.join()
        print("All watchers terminated")


    def start_file_watcher(self, filepath):
        print("Watching " + filepath)
        while self.run_threads:
            if self.check_file(filepath):
                print("Ready to send: " + filepath)
                self.send_file(filepath)
                self.filepath_list.append(filepath)
                break
            else:
                print("File still in used " + filepath)
                time.sleep(2)
                continue
        print("File sent " + filepath + "; ending filewatcher")

    def check_file(self, filepath):
        result = subprocess.run(['lsof', filepath], stdout=subprocess.PIPE)
        if len(result.stdout) > 0:
            return False
        return True

    def send_file(self, filepath):
        self.sender.send_file(filepath)







if __name__ == "__main__":
    print("running!")
    dirmon = DirectoryMonitor(".")
    dirmon.start_monitor()