# Copyright (c) 2014-2023, National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys

from tracktable.domain.terrestrial import BoundingBox
from tracktable.info import shorelines

def test_shorelines():
    north_america_medium_res = shorelines.shoreline_information(3, resolution='low', level='L1')
    assert north_america_medium_res.shape_bbox is not None

    levels = ["L1","L2","L3","L4","L5","L6"]
    for level in levels:
        if level != "L4":
            all_crude_res_shorelines = shorelines.all_shorelines(resolution='crude', level=level)
            assert len(all_crude_res_shorelines) > 0

        all_low_res_shorelines = shorelines.all_shorelines(resolution='low', level=level)
        assert len(all_low_res_shorelines) > 0

        all_medium_res_shorelines = shorelines.all_shorelines(resolution='medium', level=level)
        assert len(all_medium_res_shorelines) > 0

        all_intermediate_res_shorelines = shorelines.all_shorelines(resolution='intermediate', level=level)
        assert len(all_intermediate_res_shorelines) > 0

        # all_high_res_shorelines = shorelines.all_shorelines(resolution='high', level=level)
        # assert len(all_high_res_shorelines) > 0

        # all_full_res_shorelines = shorelines.all_shorelines(resolution='full', level=level)
        # assert len(all_full_res_shorelines) > 0

    # Shorelines around Florida
    bbox = BoundingBox((-88, 24), (-79.5, 31))
    bounding_box_shorelines = shorelines.all_shorelines_within_bounding_box(bbox)
    assert len(bounding_box_shorelines) > 0

def main():
    test_shorelines()

if __name__ == '__main__':
    sys.exit(main())
