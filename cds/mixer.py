# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Mixer extension.

"""
from __future__ import absolute_import

import json
import logging
import os
import pkg_resources
import six

from flask import current_app
from mixer.backend.flask import Mixer as _Mixer

from invenio.ext.sqlalchemy import db
from invenio.modules.search.models import Collection, CollectionCollection, \
    CollectionExample, CollectionExternalcollection, \
    CollectionFieldFieldvalue, CollectionFormat, CollectionPortalbox, \
    Collectionboxname, Collectiondetailedrecordpagetabs, Collectionname, \
    Externalcollection, Portalbox, Field, Tag, FieldTag
from invenio.modules.indexer.models import *
from invenio.modules.formatter.models import Format


# FIXME: maybe it should go somewhere else or in other way
DEFAULT_MIXER_BASE_SOURCES = 'cds'
"""Default location for the JSON files"""


class InvalidMixerRequest(Exception):

    """Docstring for InvalidMixerRequest. """

    pass


class JSONBlender(object):

    """Docstring for JSONBlender. """

    class Dump(object):

        def __init__(self, scheme):
            self.__scheme = scheme
            self.__fixtures = []
            f = pkg_resources.resource_stream(
                DEFAULT_MIXER_BASE_SOURCES, scheme.__source__)
            self.__source = open(f.name, 'w')
            f.close()

        def __enter__(self):
            return self.dump

        def __exit__(self, type, value, traceback):
            # Print ']' and close
            json.dump(self.__fixtures, self.__source, indent=4, sort_keys=True)
            self.__source.close()

        def dump(self, obj):
            """@todo: Docstring for dump.

            :param scheme: @todo
            :returns: @todo

            """
            self.__fixtures.append(obj)

    class Load(object):

        def __init__(self, scheme):
            self.__scheme = scheme
            self.__source = pkg_resources.resource_stream(
                DEFAULT_MIXER_BASE_SOURCES, scheme.__source__)

        def __enter__(self):
            return self.load

        def __exit__(self, type, value, traceback):
            self.__source.close()

        def load(self):
            """@todo: Docstring for load.

            :param scheme: @todo
            :returns: @todo

            """
            for obj in json.load(self.__source):
                yield obj


class MixerMeta(type):

    """ """

    def __new__(mcs, name, bases, dict_):
        if '__model__' not in dict_:
            raise InvalidMixerRequest(
                'Class %s does not have a __model__ specified and does not '
                'inherit from an existing Model-Mixer class')

        if '__fields__' not in dict_:
            dict_['__fields__'] = tuple(
                c.name for c in dict_['__model__'].__table__.columns)

        if '__source__' not in dict_:
            dict_['__source__'] = 'fixtures/%s.json' % (
                dict_['__model__'].__tablename__, )

        if '__blender__' not in dict_:
            dict_['__blender__'] = JSONBlender

        return super(MixerMeta, mcs).__new__(mcs, name, bases, dict_)


class Mixer(_Mixer):

    """ Custom mixer to use external files as fixtures and not only random. """

    def __init__(self, fake=True, factory=None, loglevel=logging.WARN,
                 silence=False, **params):
        super(Mixer, self).__init__(fake=fake, factory=factory,
                                    loglevel=loglevel, silence=silence)

    def blend(self, scheme, drop=True, **values):
        """@todo: Docstring for blend.

        :returns: @todo

        """
        result = []

        if drop:
            scheme.__model__.query.delete()

        with scheme.__blender__.Load(scheme) as load:
            for fixture_values in load():
                fixture_values.update(values)
                result.append(
                    super(Mixer, self).blend(scheme.__model__,
                                             **fixture_values)
                )
        return result

    def unblend(self, scheme, *criterion):
        """@todo: Docstring for unblend.

        :returns: @todo

        """
        with scheme.__blender__.Dump(scheme) as dump:
            for row in scheme.__model__.query.filter(*criterion):
                dump(dict((key, value) for (key, value) in row.todict()
                          if key in scheme.__fields__))

# FIXME: Factor out!!!!


class ExternalcollectionMixer(six.with_metaclass(MixerMeta)):
    __model__ = Externalcollection


class CollectiondetailedrecordpagetabsMixer(six.with_metaclass(MixerMeta)):
    __model__ = Collectiondetailedrecordpagetabs


class CollectionMixer(six.with_metaclass(MixerMeta)):
    __model__ = Collection
    __fields__ = ('id', 'name', 'dbquery')


class CollectionCollectionMixer(six.with_metaclass(MixerMeta)):
    __model__ = CollectionCollection


class CollectionFieldFieldvalueMixer(six.with_metaclass(MixerMeta)):
    __model__ = CollectionFieldFieldvalue


class CollectionFormatMixer(six.with_metaclass(MixerMeta)):
    __model__ = CollectionFormat


class PortalboxMixer(six.with_metaclass(MixerMeta)):
    __model__ = Portalbox


class CollectionnameMixer(six.with_metaclass(MixerMeta)):
    __model__ = Collectionname


class CollectionboxnameMixer(six.with_metaclass(MixerMeta)):
    __model__ = Collectionboxname


class FieldMixer(six.with_metaclass(MixerMeta)):
    __model__ = Field


class FieldTagMixer(six.with_metaclass(MixerMeta)):
    __model__ = FieldTag


class TagMixer(six.with_metaclass(MixerMeta)):
    __model__ = Tag


class FormatMixer(six.with_metaclass(MixerMeta)):
    __model__ = Format


class IdxINDEXMixer(six.with_metaclass(MixerMeta)):
    __model__ = IdxINDEX


class IdxINDEXFieldMixer(six.with_metaclass(MixerMeta)):
    __model__ = IdxINDEXField


class IdxINDEXNAMEMixer(six.with_metaclass(MixerMeta)):
    __model__ = IdxINDEXNAME


class IdxINDEXIdxINDEXMixer(six.with_metaclass(MixerMeta)):
    __model__ = IdxINDEXIdxINDEX

MIXERS = {
    'collection': CollectionMixer,
    'collection_collection': CollectionCollectionMixer,
    'collectionboxname': CollectionboxnameMixer,
    'collectionname': CollectionnameMixer,
    'externalcollection': ExternalcollectionMixer,
    'collectiondetailedrecordpagetabs': CollectiondetailedrecordpagetabsMixer,
    'collection_field_fieldvalue': CollectionFieldFieldvalueMixer,
    'collection_format': CollectionFormatMixer,
    'portalbox': PortalboxMixer,
    'field': FieldMixer,
    'field_tag': FieldTagMixer,
    'tag': TagMixer,
    'format': FormatMixer,
    'idxINDEX': IdxINDEXMixer,
    'idxINDEXNAME': IdxINDEXNAMEMixer,
    'idxINDEX_field': IdxINDEXFieldMixer,
    'idxINDEX_idxINDEX': IdxINDEXIdxINDEXMixer
}
""" Registry like."""

mixer = Mixer()
mixer.init_app(current_app)


def blend():
    for table in db.metadata.sorted_tables:
        if table.name in MIXERS:
            mixer.blend(MIXERS[table.name])

def unblend():
    for table in db.metadata.sorted_tables:
        if table.name in MIXERS:
            mixer.unblend(MIXERS[table.name])

