'''
Copyright (C) 2018 Samy Tichadou (tonton)
samytichadou@gmail.com

Created by Samy Tichadou (tonton)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


# IMPORT
##################################

from . import (
    addon_prefs,
    manage_presets,
    apply_preset,
    gui,
    )

# register
##################################

def register():
    addon_prefs.register()
    manage_presets.register()
    apply_preset.register()
    gui.register()


def unregister():
    addon_prefs.unregister()
    manage_presets.unregister()
    apply_preset.unregister()
    gui.unregister()
