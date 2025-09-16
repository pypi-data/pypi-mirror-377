######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.5                                                                                 #
# Generated on 2025-09-16T00:24:37.032406                                                            #
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

