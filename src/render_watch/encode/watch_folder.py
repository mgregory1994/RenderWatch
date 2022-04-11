# Copyright 2022 Michael Gregory
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


class WatchFolderInstance:
    """Class that configures a watch folder instance that finds new files that are added to a directory."""

    def __init__(self, folder_directory):
        """
        Initializes the WatchFolderInstance class with the variables necessary for
        queueing new files found in the given directory and keeping track of files that have already been found and
        files that have been removed.

        Parameters:
            folder_directory: Directory to create a watch folder instance from.
        """
        self._folder_directory = folder_directory
        self._new_files_queue = queue.Queue()
        self._files_found_in_folder = []
        self.event_handler = PatternMatchingEventHandler('*', '', True, True)
        self.event_handler.on_created = self._on_folder_contents_changed
        self.event_handler.on_deleted = self._remove_deleted_files
        self.observer = None
        self._add_new_files()

    @property
    def queue(self) -> queue.Queue:
        """
        Returns a queue of new files found in the watch folder instance's directory.

        Returns:
            Queue that contains new files found in the watch folder instance's directory.
        """
        return self._new_files_queue

    @property
    def path(self) -> str:
        """
        Returns the watch folder instance's directory.

        Returns:
            String that represents the watch folder instance's directory.
        """
        return self._folder_directory

    def _on_folder_contents_changed(self, event):  # Unused parameter needed
        # Runs a thread that checks for new files when the watch folder instance's contents change.
        threading.Thread(target=self._add_new_files, args=(), daemon=True).start()

        logging.info('--- WATCH FOLDER CONTENTS CHANGED: ' + self.path + ' ---')

    def _add_new_files(self):
        # Checks the watch folder instance's directory for new files and adds them to the new files queue.
        for file_name in os.listdir(self._folder_directory):
            if os.path.isdir(os.path.join(self._folder_directory, file_name)):
                continue

            if file_name not in self._files_found_in_folder:
                file_path = os.path.join(self._folder_directory, file_name)
                file_size = os.path.getsize(file_path)

                time.sleep(1)

                self._wait_on_file_size_changing(file_path, file_size)
                self._add_new_file_to_instance(file_path, file_name)

    @staticmethod
    def _wait_on_file_size_changing(file_path: str, file_size: int):
        # Blocks the calling thread if the given file's size is changing over time.
        while file_size != os.path.getsize(file_path):
            file_size = os.path.getsize(file_path)

            time.sleep(1)

    def _add_new_file_to_instance(self, file_path: str, file_name: str):
        # Adds the new file path to the new files queue and adds the file name to the found files list.
        self._files_found_in_folder.append(file_name)
        self._new_files_queue.put(file_path)

    def _remove_deleted_files(self, event):  # Unused parameter needed
        # Processes any files have been removed from the watch folder instance's directory.
        for file_name in self._files_found_in_folder:
            file_path = os.path.join(self._folder_directory, file_name)

            if not os.path.exists(file_path):
                self._files_found_in_folder.remove(file_name)

                logging.info('--- WATCH FOLDER FILE REMOVED: ' + file_path + ' ---')


class WatchFolderScheduler:
    """Class that configures the scheduler for watch folder directories."""

    def __init__(self):
        """
        Initializes the WatchFolderScheduler class with the variables necessary for scheduling watch folder instances.
        """
        self._instances = {}
        self._observer = Observer()
        self._observer.start()

    def add_folder_path(self, folder_directory: str):
        """
        Sets up a watch folder instance using the given folder directory.

        Parameters:
            folder_directory: Directory to create a watch folder instance from.

        Returns:
            None
        """
        watch_folder_instance = WatchFolderInstance(folder_directory)
        self._instances[folder_directory] = watch_folder_instance
        watch_folder_instance.observer = self._observer.schedule(watch_folder_instance.event_handler,
                                                                 folder_directory,
                                                                 recursive=False)

    def get_instance(self, folder_directory: str) -> WatchFolderInstance | None:
        """
        Returns the watch folder instance for the given folder directory or None if there is no
        instance for the given directory.

        Parameters:
            folder_directory: Folder directory to get a watch folder instance from.

        Returns:
            Watch folder instance for the given folder directory or None if there is no watch folder instance
            for the given folder directory.
        """
        try:
            return self._instances[folder_directory].queue.get()
        except KeyError:
            return None

    def is_instance_empty(self, folder_directory: str) -> bool:
        """
        Checks if the watch folder instance for the folder directory has found any new files.

        Parameters:
            folder_directory: Directory to get a watch folder instance from.

        Returns:
            Boolean that represents whether the watch folder instance for the folder directory has found any new files.
        """
        try:
            watch_folder_instance = self._instances[folder_directory]
            return watch_folder_instance.queue.empty()
        except KeyError:
            return True

    def stop_and_remove_instance(self, folder_directory: str):
        """
        Stops the watch folder instance for the folder directory and removes it from the scheduler.

        Parameters:
            folder_directory: Directory to get a watch folder instance from.
        """
        try:
            watch_folder_instance = self._instances[folder_directory]
            watch_folder_instance.queue.put(False)
            self._observer.unschedule(watch_folder_instance.observer)
        except KeyError:
            logging.exception('--- FAILED TO STOP AND REMOVE WATCH FOLDER INSTANCE ---')
