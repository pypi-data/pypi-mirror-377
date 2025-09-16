######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.5.1+obcheckpoint(0.2.4);ob(v1)                                                    #
# Generated on 2025-09-16T01:38:51.294033                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

class NotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    ...

