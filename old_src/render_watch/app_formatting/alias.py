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


from datetime import datetime


counter = -1


class AliasGenerator:

    global counter

    @staticmethod
    def generate_alias_from_name(name):
        """
        Creates a unique alias based off of the first character of the name.

        :param name: Name to generate an alias from.
        """
        global counter
        counter += 1

        current_date_time = datetime.now().strftime('_%m-%d-%Y_%H%M%S')

        return name[0] + str(counter) + current_date_time
