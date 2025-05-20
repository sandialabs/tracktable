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
from tracktable.info import rivers

def test_rivers():
    river_info = rivers.river_information(3, resolution='low', level='L01')
    assert river_info.shape_bbox is not None

    levels = ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11"]
    for level in levels:
        all_crude_res_rivers = rivers.all_rivers(resolution='crude', level=level)
        assert len(all_crude_res_rivers) > 0

        all_low_res_rivers = rivers.all_rivers(resolution='low', level=level)
        assert len(all_low_res_rivers) > 0

        all_medium_res_rivers = rivers.all_rivers(resolution='medium', level=level)
        assert len(all_medium_res_rivers) > 0

        all_intermediate_res_rivers = rivers.all_rivers(resolution='intermediate', level=level)
        assert len(all_intermediate_res_rivers) > 0

        # all_high_res_rivers = rivers.all_rivers(resolution='high', level=level)
        # assert len(all_high_res_rivers) > 0

        # all_full_res_rivers = rivers.all_rivers(resolution='full', level=level)
        # assert len(all_full_res_rivers) > 0

    # Rivers in Florida
    bbox = BoundingBox((-88, 24), (-79.5, 31))
    bounding_box_rivers = rivers.all_rivers_within_bounding_box(bbox, level="L03")
    assert len(bounding_box_rivers) > 0

def main():
    test_rivers()

if __name__ == '__main__':
    sys.exit(main())
