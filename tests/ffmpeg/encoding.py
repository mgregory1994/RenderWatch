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


import threading
import time
import random

from render_watch.ffmpeg import encoding


RANDOM_BITRATE = (5245.6, 7655.2, 9009.3, 2110.7, 981.0, 3335.9, 5509.2, 4467.7, 3097.3, 6208.3)
RANDOM_SPEED = (1.0, 2.45, 2.3, 4.1, 0.8, 0.9, 2.2, 3.1, 5.6, 7.1, 4.2, 5.4, 0.6, 1.3, 1.8, 2.1)
RANDOM_FILE_SIZE = ('10.5MB', '12.6MB', '4.2GB', '90.2MB', '554.2KB', '456.3MB', '10.4GB')


class TestTask:
    def __init__(self):
        self.task = encoding.Task('/some/test/dir')

    def run_test(self):
        threading.Thread(target=self.encoder_instance, args=(self.task,)).start()
        time.sleep(int(random.randint(1, 30) / 10.0))
        threading.Thread(target=self.info_timer_instance, args=(self.task,)).start()

    @staticmethod
    def encoder_instance(task: encoding.Task):
        task.has_started = True
        count = 0

        while not (task.is_done or task.is_stopped):
            try:
                task.bitrate = random.choice(RANDOM_BITRATE)
                task.speed = random.choice(RANDOM_SPEED)
                task.file_size = random.choice(RANDOM_FILE_SIZE)
                task.time_left_in_seconds = 30 - count

                count += 1
                time.sleep(1)

                if count >= 30:
                    task.is_done = True
            except Exception as e:
                print(e)
                continue

    @staticmethod
    def info_timer_instance(task: encoding.Task):
        bitrate = None
        speed = None
        file_size = None
        task_time_left = None

        while not (task.is_done or task.is_stopped):
            try:
                bitrate = str(task.bitrate) + 'bkps'
                speed = str(task.speed) + 'x'
                file_size = task.file_size
                task_time_left = str(task.time_left_in_seconds) + 's'

                print(
                    'Has Started: ', str(task.has_started), '\n',
                    'Is Stopped: ', str(task.is_stopped), '\n',
                    'Is Paused: ', str(task.is_paused), '\n',
                    'Is Done: ', str(task.is_done), '\n',
                    'bitrate: ', bitrate, '\n',
                    'speed: ', speed, '\n',
                    'File Size: ', file_size, '\n',
                    'Time Left: ', task_time_left, '\n'
                )

                time.sleep(1)
            except Exception as e:
                print(e)
                continue

        print(
            'Has Started: ', str(task.has_started), '\n',
            'Is Stopped: ', str(task.is_stopped), '\n',
            'Is Paused: ', str(task.is_paused), '\n',
            'Is Done: ', str(task.is_done), '\n',
            'bitrate: ', bitrate, '\n',
            'speed: ', speed, '\n',
            'File Size: ', file_size, '\n',
            'Time Left: ', task_time_left, '\n'
        )


if __name__ == '__main__':
    test_task = TestTask()
    test_task.run_test()
