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


class UIHelper:
    """Contains methods for setting up Gtk widgets."""

    @staticmethod
    def setup_combobox(combobox, entries_list):
        """Builds the given combobox by adding the given entries to the combobox.

        The combobox is set up to select the first item in the entries list.

        :param combobox:
            Gtk.Combobox widget.
        :param entries_list:
            List of entries for combobox.
        """
        for value in entries_list:
            combobox.append_text(value)
        combobox.set_entry_text_column(0)
        combobox.set_active(0)

    @staticmethod
    def rebuild_combobox(combobox, entries_list):
        """Rebuilds an already built combobox using the given entries list.

        The original entires for the combobox are remove first before adding the new entries list.

        :param combobox:
            Gtk.Combobox widget.
        :param entries_list:
            List of entries for combobox.
        """
        combobox.remove_all()
        for entry in entries_list:
            combobox.append_text(entry)
        combobox.set_entry_text_column(0)
        combobox.set_active(0)
