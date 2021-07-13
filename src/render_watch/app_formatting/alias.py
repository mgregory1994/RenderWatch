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


counter = -1


class AliasGenerator:

    global counter

    @staticmethod
    def generate_alias_from_name(name):
        """Use the first character of the name and concatenate the global counter to make an alias name.

        The global counter is incremented each time this function is called in order to keep all generated
        aliases unique.

        :param name:
            Name string to generate an alias from.
        """
        global counter
        counter += 1

        alias = name[0] + '_' + str(counter)
        return alias
