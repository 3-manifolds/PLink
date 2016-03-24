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
"""
This module exports the Crossing class, which represents a crossing
in a link diagram, and the ECrossing class which represents an edge
of the diagram passing through a crossing.
"""
class Crossing:
    """
    A pair of crossing arrows in a PL link diagram.
    """
    def __init__(self, over, under, is_virtual=False, label=None):
        self.over = over
        self.under = under
        self.locked = False
        self.KLP = {}    # See the SnapPea file link_projection.h
        self.hit1 = None # For computing DT codes
        self.hit2 = None
        self.comp1 = None
        self.comp2 = None
        self.flipped = None
        self.is_virtual = is_virtual
        self.locate()
        self.label = label

    def __repr__(self):
        self.locate()
        if not self.is_virtual:
            return '%s over %s at (%s,%s)'%(
                self.over, self.under, self.x, self.y)
        else:
            return 'virtual crossing of %s and %s at (%s,%s)'%(
                self.over, self.under, self.x, self.y)
            
    def __eq__(self, other):
        """
        Crossings are equivalent if they involve the same arrows.
        """
        if self.over in other and self.under in other:
            return True
        else:
            return False

    def __hash__(self):
        # Since we redefined __eq__ we need to define __hash__
        return id(self)
        
    def __contains__(self, arrow):
        if arrow == None or arrow == self.over or arrow == self.under:
            return True
        else:
            return False
        
    def locate(self):
        t = self.over ^ self.under
        if t:
            self.x = self.over.start.x + t*self.over.dx
            self.y = self.over.start.y + t*self.over.dy
        else:
            #print 'Crossing.locate failed'
            #print 'over = %s, under = %s'%(self.over, self.under)
            self.x = self.y = None

    def sign(self):
        try:
            D = self.under.dx*self.over.dy - self.under.dy*self.over.dx
            if D > 0: return 'RH'
            if D < 0: return 'LH'
        except:
            return 0

    def strand(self, arrow):
        sign = self.sign()
        if arrow not in self:
            return None
        elif ( (arrow == self.over and sign == 'RH') or
               (arrow == self.under and sign =='LH') ):
            return 'X'
        else:
            return 'Y'

    def reverse(self):
        self.over, self.under = self.under, self.over

    def height(self, arrow):
        if arrow == self.under:
            return self.under ^ self.over
        elif arrow == self.over:
            return self.over ^ self.under
        else:
            return None

    def DT_hit(self, count, ecrossing):
        """
        Count the crossing, using DT conventions.  Return True on the
        first hit if the count is odd and the crossing is shared by
        two components of the diagram.  As a side effect, set the
        flipped attribute on the first hit.
        """
        over = ecrossing.goes_over()
        if count%2 == 0 and over:
            count = -count
        if self.hit1 == 0:
            self.hit1 = count
            sign = self.sign()
            if sign:
                self.flipped = over ^ (sign == 'RH')
            if count%2 != 0 and self.comp1 != self.comp2:
                return True
        elif self.hit2 == 0:
            self.hit2 = count
        else:
            raise ValueError('Too many hits!')

    def mark_component(self, component):
        if self.comp1 is None:
            self.comp1 = component
        elif self.comp2 is None:
            self.comp2 = component
        else:
            raise ValueError('Too many component hits!')

    def clear_marks(self):
        self.hit1= self.hit2 = 0
        self.flipped = self.comp1 = self.comp2 = None

class ECrossing:
    """
    A pair: (Crossing, Arrow), where the Arrow is involved in the Crossing.
    The ECrossings correspond 1-1 with edges of the link diagram.
    """ 
    def __init__(self, crossing, arrow):
        if arrow not in crossing:
            raise ValueError
        self.crossing = crossing
        self.arrow = arrow
        self.strand = self.crossing.strand(self.arrow)

    def pair(self):
        return (self.crossing, self.arrow)

    def goes_over(self):
        if self.arrow == self.crossing.over:
            return True
        return False


