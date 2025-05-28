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
from tracktable.info import ports

def test_ports():
    alexandria_port = ports.port_information("Alexandria")
    assert alexandria_port.world_port_index_number != None
    assert alexandria_port.region != None
    assert alexandria_port.name != None
    assert alexandria_port.name == 'Alexandria'
    assert alexandria_port.alternate_name != None
    assert alexandria_port.un_locode != None
    assert alexandria_port.country != None
    assert alexandria_port.country == 'United States'
    assert alexandria_port.water_body != None
    assert alexandria_port.position != None
    assert len(alexandria_port.attributes) > 0

    newport_port = ports.port_information("newport")
    assert type(newport_port) == list

    newport_port = ports.port_information("newport", country='United Kingdom')
    assert newport_port.name == 'Newport' and newport_port.country == 'United Kingdom'

    new_shoreham_port = ports.port_information("New Shoreham")
    assert new_shoreham_port.alternate_name == 'New Shoreham' and new_shoreham_port.country == 'United Kingdom'

    united_states_ports = ports.all_ports_by_country("United States")
    assert len(united_states_ports) > 0

    pacific_ocean_ports = ports.all_ports_by_water_body("Pacific Ocean")
    assert len(pacific_ocean_ports) > 0

    wpi_region_wales_ports = ports.all_ports_by_wpi_region("Wales -- 34710")
    assert len(wpi_region_wales_ports) == 10

    wpi_region_wales_ports = ports.all_ports_by_wpi_region("Wales")
    assert len(wpi_region_wales_ports) == 10

    wpi_region_wales_ports = ports.all_ports_by_wpi_region("34710")
    assert len(wpi_region_wales_ports) == 10

    wpi_region_wales_ports = ports.all_ports_by_wpi_region(34710)
    assert len(wpi_region_wales_ports) == 10

    # Ports around Florida
    bbox = BoundingBox((-88, 24), (-79.5, 31))
    bounding_box_ports = ports.all_ports_within_bounding_box(bbox)
    assert len(bounding_box_ports) > 0

def main():
    test_ports()

if __name__ == '__main__':
    sys.exit(main())
