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
    """Creates and manages watch folder instances."""

    def __init__(self):
        self.__watch_folder_instances = {}
        self.__watch_folder_observer = Observer()
        self.__watch_folder_observer.start()

    def add_folder_path(self, folder_path):
        """Sets up a watch folder instance using the folder path.

        :param folder_path:
            The absolute path of the folder.
        """
        watch_folder_instance = WatchFolderInstance(folder_path)
        self.__watch_folder_instances[folder_path] = watch_folder_instance
        watch_folder_instance.watch = self.__watch_folder_observer.schedule(watch_folder_instance.event_handler,
                                                                            folder_path,
                                                                            recursive=False)

    def get_instance(self, folder_path):
        """Returns the watch folder instance for the folder path.

        :param folder_path:
            The absolute path of the folder.
        """
        try:
            return self.__watch_folder_instances[folder_path].queue.get()
        except KeyError:
            return None

    def is_instance_empty(self, folder_path):
        """Checks if the watch folder instance for the folder path has found any new files.

        :param folder_path:
            The absolute path of the folder.
        """
        try:
            watch_folder_instance = self.__watch_folder_instances[folder_path]
            return watch_folder_instance.queue.empty()
        except KeyError:
            return True

    def stop_and_remove_instance(self, folder_path):
        """Stops the watch folder instance for the folder path and removes it.

        :param folder_path:
            The absolute path of the folder.
        """
        try:
            watch_folder_instance = self.__watch_folder_instances[folder_path]
            watch_folder_instance.queue.put(False)
            self.__watch_folder_observer.unschedule(watch_folder_instance.watch)
            return True
        except KeyError:
            logging.exception('--- FAILED TO STOP AND REMOVE WATCH FOLDER INSTANCE ---')
            return False


class WatchFolderInstance:
    """Watches a folder directory for contents changed."""

    def __init__(self, folder_path):
        self.__folder_path = folder_path
        self.__watch_folder_queue = queue.Queue()
        self.__files_in_folder_list = []
        self.__event_handler = PatternMatchingEventHandler('*', '', True, True)
        self.__event_handler.on_created = self.__on_folder_contents_changed
        self.__event_handler.on_deleted = self.__check_for_deleted_files
        self.watch = None
        self.__check_and_add_files_in_folder()

    @property
    def queue(self):
        return self.__watch_folder_queue

    @property
    def path(self):
        return self.__folder_path

    @property
    def event_handler(self):
        return self.__event_handler

    def __on_folder_contents_changed(self, event):  # Unused parameter needed
        # Starts a thread to add any new files in the folder's directory.
        threading.Thread(target=self.__check_and_add_files_in_folder, args=(), daemon=True).start()

        logging.info('--- WATCH FOLDER CONTENTS CHANGED: ' + self.path + ' ---')

    def __check_and_add_files_in_folder(self):
        # Gets list of files in the folder's directory
        # and checks if there are any new files.
        files_in_folder = os.listdir(self.__folder_path)
        self.__add_new_files(files_in_folder)

    def __add_new_files(self, files_in_folder):
        # Checks if there are any new files in our list of known files.
        for file in files_in_folder:
            if file not in self.__files_in_folder_list:
                file_path = os.path.join(self.__folder_path, file)
                file_size = os.path.getsize(file_path)

                time.sleep(1)

                self.__wait_for_file_size_changing(file_path, file_size)
                self.__add_new_file_to_instance(file, file_path)

    @staticmethod
    def __wait_for_file_size_changing(file_path, file_size):
        # Wait until the file is done copying
        while file_size != os.path.getsize(file_path):
            file_size = os.path.getsize(file_path)

            time.sleep(1)

    def __add_new_file_to_instance(self, file, file_path):
        self.__files_in_folder_list.append(file)
        self.__watch_folder_queue.put(file_path)

    def __check_for_deleted_files(self, event):  # Unused parameter needed
        # When a file is removed from the folder's directory,
        # remove it from our list of known files.
        for file in self.__files_in_folder_list:
            file_path = os.path.join(self.__folder_path, file)
            if not os.path.exists(file_path):
                self.__files_in_folder_list.remove(file)

                logging.info('--- WATCH FOLDER FILE REMOVED: ' + file_path + ' ---')
