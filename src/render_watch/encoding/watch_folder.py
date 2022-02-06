# Copyright 2021 Michael Gregory
#
# This file is part of Render Watch.
#
# Render Watch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Render Watch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.


import os
import queue
import threading
import time
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class WatchFolder:
    """
    Creates and manages watch folder instances.
    """

    def __init__(self):
        self._watch_folder_instances = {}
        self._watch_folder_observer = Observer()
        self._watch_folder_observer.start()

    def add_folder_path(self, folder_path):
        """
        Sets up a watch folder instance using the folder path.

        :param folder_path: The absolute path of the folder.
        """
        watch_folder_instance = WatchFolderInstance(folder_path)
        self._watch_folder_instances[folder_path] = watch_folder_instance
        watch_folder_instance.watch = self._watch_folder_observer.schedule(watch_folder_instance.event_handler,
                                                                           folder_path,
                                                                           recursive=False)

    def get_instance(self, folder_path):
        """
        Returns the watch folder instance for the folder path.

        :param folder_path: The absolute path of the folder.
        """
        try:
            return self._watch_folder_instances[folder_path].queue.get()
        except KeyError:
            return None

    def is_instance_empty(self, folder_path):
        """
        Checks if the watch folder instance for the folder path has found any new files.

        :param folder_path: The absolute path of the folder.
        """
        try:
            watch_folder_instance = self._watch_folder_instances[folder_path]
            return watch_folder_instance.queue.empty()
        except KeyError:
            return True

    def stop_and_remove_instance(self, folder_path):
        """
        Stops the watch folder instance for the folder path and removes it.

        :param folder_path: The absolute path of the folder.
        """
        try:
            watch_folder_instance = self._watch_folder_instances[folder_path]
            watch_folder_instance.queue.put(False)
            self._watch_folder_observer.unschedule(watch_folder_instance.watch)

            return True
        except KeyError:
            logging.exception('--- FAILED TO STOP AND REMOVE WATCH FOLDER INSTANCE ---')

            return False


class WatchFolderInstance:
    """
    Watches a folder directory for changed contents.
    """

    def __init__(self, folder_path):
        self._folder_path = folder_path
        self._watch_folder_queue = queue.Queue()
        self._files_found_in_folder = []
        self.event_handler = PatternMatchingEventHandler('*', '', True, True)
        self.event_handler.on_created = self._on_folder_contents_changed
        self.event_handler.on_deleted = self._remove_deleted_files
        self.watch = None
        self._add_new_files()

    @property
    def queue(self):
        return self._watch_folder_queue

    @property
    def path(self):
        return self._folder_path

    def _on_folder_contents_changed(self, event):  # Unused parameter needed
        threading.Thread(target=self._add_new_files, args=(), daemon=True).start()

        logging.info('--- WATCH FOLDER CONTENTS CHANGED: ' + self.path + ' ---')

    def _add_new_files(self):
        for file in os.listdir(self._folder_path):
            if os.path.isdir(os.path.join(self._folder_path, file)):
                print(os.path.join(self._folder_path, file), 'is a directory')
                continue
            else:
                print(os.path.join(self._folder_path, file), 'is not a directory')

            if file not in self._files_found_in_folder:
                file_path = os.path.join(self._folder_path, file)
                file_size = os.path.getsize(file_path)

                time.sleep(1)

                self._wait_on_file_size_changing(file_path, file_size)
                self._add_new_file_to_instance(file, file_path)

    @staticmethod
    def _wait_on_file_size_changing(file_path, file_size):
        while file_size != os.path.getsize(file_path):
            file_size = os.path.getsize(file_path)

            time.sleep(1)

    def _add_new_file_to_instance(self, file, file_path):
        self._files_found_in_folder.append(file)
        self._watch_folder_queue.put(file_path)

    def _remove_deleted_files(self, event):  # Unused parameter needed
        for file in self._files_found_in_folder:
            file_path = os.path.join(self._folder_path, file)
            if not os.path.exists(file_path):
                self._files_found_in_folder.remove(file)

                logging.info('--- WATCH FOLDER FILE REMOVED: ' + file_path + ' ---')
