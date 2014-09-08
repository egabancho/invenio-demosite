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

from six import with_metaclass as meta

from invenio.ext.mixer import MixerMeta
from invenio.modules.indexer.models import IdxINDEX, IdxINDEXNAME, \
    IdxINDEXField, IdxINDEXIdxINDEX
from invenio.modules.search.models import Field, Tag, FieldTag


class IdxINDEXMixer(meta(MixerMeta)):
    __model__ = IdxINDEX


class IdxINDEXFieldMixer(meta(MixerMeta)):
    __model__ = IdxINDEXField


class IdxINDEXNAMEMixer(meta(MixerMeta)):
    __model__ = IdxINDEXNAME


class IdxINDEXIdxINDEXMixer(meta(MixerMeta)):
    __model__ = IdxINDEXIdxINDEX


__all__ = ('IdxINDEXMixer', 'IdxINDEXFieldMixer', 'IdxINDEXNAMEMixer',
           'IdxINDEXIdxINDEXMixer', )
