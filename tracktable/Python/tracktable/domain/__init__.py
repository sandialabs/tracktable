#
# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
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

"""Tracktable Trajectory Library - Domains module

Here you will find the modules containing point, trajectory and reader
types for each different point domain.

"""

import importlib

all_domains = ['terrestrial', 'cartesian2d', 'cartesian3d']


def domain_module_from_name(_domain):
    """domain_module_from_name(name: string) -> domain module

    Given the name of one of Tracktable's point domains 
    (terrestrial, cartesian2d, cartesian3d), return the
    module object for that domain.

    This helps you retrieve related classes for a domain object
    when you don't know the domain a priori.

    Arguments:
        _domain [string]: Name of point domain

    Returns:
        Module object for specified domain

    Raises:
        AttributeError: you've asked for a domain that
            doesn't exist
    """
    global all_domains
    domain = _domain.lower()
    if domain not in all_domains:
        raise KeyError(('Requested domain {} is not in list of '
                        'available domains: {}').format(_domain,
                                                        all_domains))
    domain_to_import = 'tracktable.domain.{}'.format(domain)
    domain_module = importlib.import_module(domain_to_import)
    return domain_module


def domain_module_for_object(thing):
    """domain_module_for_object(thing: object) -> domain module

    Given a Tracktable object (point, trajectory point, trajectory
    or bounding box), return the module for that object's point
    domain.

    This helps you retrieve related classes for a domain object
    if you don't know the domain a priori.

    Arguments:
        thing (object): Tracktable domain object

    Returns:
        Module object for that point's domain

    Raises:
        AttributeError: you supplied an object that does not have
            a 'domain' attribute
    """
    try:
        desired_domain = thing.domain
        domain_module = domain_module_from_name(desired_domain)
        return domain_module
    except AttributeError as e:
        raise AttributeError((
            "Object of type {} does not have a 'domain'"
            " attribute.  Are you sure this is a Tracktable "
            "point, trajectory, or bounding box?"
            ).format(type(thing))) from e

def domain_class_for_object(thing, desired_class):
    """domain_class_for_object(thing: object, class_name: string) -> class object

    Given a Tracktable object (point, trajectory point, trajectory
    or bounding box) and the name of a related class, return the class
    object for that related class.

    This helps you retrieve related classes for a domain object
    if you don't know the domain a priori.  For example, if the user
    wants a bounding box for some arbitrary trajectory, you can ask
    for "whatever BoundingBox type corresponds to this object".

    Arguments:
        thing (object): Tracktable domain object
        desired_class (string): Name of desired class

    Returns:
        Class object for the requested class

    Raises:
        AttributeError: you supplied an object that does not have
            a 'domain' attribute or asked for a domain class that
            does not exist

    """
    domain = domain_module_for_object(thing)
    if desired_class not in [
          "BasePoint", "TrajectoryPoint", "Trajectory", "BoundingBox"
          ]:
        raise AttributeError((
            "There is no domain class called '{}' in Tracktable."
            ).format(desired_class))
    else:
        return getattr(domain, desired_class)
