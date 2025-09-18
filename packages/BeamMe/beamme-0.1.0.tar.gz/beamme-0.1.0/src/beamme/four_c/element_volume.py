# The MIT License (MIT)
#
# Copyright (c) 2018-2025 BeamMe Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""This file implements volume elements for 4C."""

from beamme.core.element_volume import VolumeElement as _VolumeElement


class SolidRigidSphere(_VolumeElement):
    """A rigid sphere solid element."""

    def __init__(self, **kwargs):
        """Initialize solid sphere object."""
        _VolumeElement.__init__(self, **kwargs)

        self.radius = float(self.data["RADIUS"])

    # TODO this method should be removed!
    # This method should use the super method of _VolumeElement
    # but currently this results in a circular import if we use the
    # element to 4C mappings. Think about a better solution.
    def dump_to_list(self):
        """Return a dict with the items representing this object."""

        return {
            "id": self.i_global + 1,
            "cell": {
                "type": "POINT1",
                "connectivity": self.nodes,
            },
            "data": self.data,
        }
