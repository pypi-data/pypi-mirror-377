######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.6                                                                                 #
# Generated on 2025-09-17T19:37:30.037075                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

