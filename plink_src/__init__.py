#!/usr/bin/env python
#
#   Copyright (C) 2007-present Marc Culler, Nathan Dunfield and others.
#
#   This program is distributed under the terms of the 
#   GNU General Public License, version 2 or later, as published by
#   the Free Software Foundation.  See the file gpl-2.0.txt for details.
#   The URL for this program is
#     http://www.math.uic.edu/~t3m/plink
#   A copy of the license file may be found at:
#     http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
#   The development of this program was partially supported by
#   the National Science Foundation under grants DMS0608567,
#   DMS0504975 and DMS0204142.

from . import version as __version__
from .manager import LinkManager
from .viewer import LinkViewer
from .editor import LinkEditor
__all__ = ['LinkManager', 'LinkViewer', 'LinkEditor']

if __name__ == '__main__':
    LE = LinkEditor()
    LE.window.mainloop()
