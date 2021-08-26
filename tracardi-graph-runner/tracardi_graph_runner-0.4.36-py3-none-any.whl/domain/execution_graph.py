import asyncio
import importlib
import inspect
from time import time
from typing import List, Union
from pydantic import BaseModel
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.console import Console
from tracardi_plugin_sdk.domain.result import Result, VoidResult, MissingResult

from .debug_call_info import DebugCallInfo, DebugOutput, DebugInput, Profiler
from .debug_info import DebugInfo, DebugNodeInfo, FlowDebugInfo, DebugEdgeInfo
from .entity import Entity
from .init_result import InitResult
from .input_params import InputParams
from ..utils.dag_error import DagError, DagExecError
from .edge import Edge
from .node import Node
from .tasks_results import ActionsResults


class ExecutionGraph(BaseModel):
    graph: List[Node]
    start_nodes: list
    debug: bool = False

    @staticmethod
    def _add_to_event_loop(tasks, coroutine, port, params, edge_id, active) -> list:
        task = asyncio.create_task(coroutine)
        tasks.append((task, port, params, edge_id, active))
        return tasks

    @staticmethod
    async def _void_return(node):

        all_outputs = [VoidResult(port=_start_port, value=None)
                       for _start_port in node.graph.out_edges.get_start_ports()]

        outputs_len = len(all_outputs)

        if outputs_len == 0:
            return None
        elif len(all_outputs) == 1:
            return all_outputs[0]
        else:
            return tuple(all_outputs)

    @staticmethod
    def _null_params(node):
        pass

    def _run_in_event_loop(self, tasks, node, params, _port, _task_result, edge_id):
        try:
            coroutine = node.object.run(**params)
            return self._add_to_event_loop(tasks,
                                           coroutine,
                                           port=_port,
                                           params=_task_result,
                                           edge_id=edge_id,
                                           active=True)
        except TypeError as e:
            args_spec = inspect.getfullargspec(node.object.run)
            method_params = args_spec.args[1:]
            if not set(method_params).intersection(set(params.keys())):
                raise DagExecError(
                    "Misconfiguration of node type `{}`. Method `run` expects input parameters `{}`, but received `{}`. "
                    "TypeError: `{}`".
                        format(node.className,
                               ",".join(method_params),
                               ",".join(params.keys()),
                               str(e))
                )

    async def run_task(self, node: Node, payload, ready_upstream_results: ActionsResults):

        task_start_time = time()

        if isinstance(node.object, DagExecError):
            raise node.object

        tasks = []

        if node.start:

            # This is first node in graph.
            # During debugging debug nodes are removed.

            _port = "void"
            _payload = {}

            params = {"void": payload}
            tasks = self._run_in_event_loop(tasks, node, params, _port, _payload, None)

        elif node.graph.in_edges:

            # Prepare value

            for start_port, edge, end_port in node.graph.in_edges:  # type: str, Edge, str

                if not ready_upstream_results.has_edge_value(edge.id):
                    # This edge is dead. Dead edges are connected to nodes that return None instead of Result object.
                    continue

                for upstream_result in ready_upstream_results.get(
                        edge.id,
                        start_port):  # type: Union[Result]

                    if isinstance(upstream_result, MissingResult):

                        # Missing result

                        void_result_coroutine = self._void_return(node)

                        # The original run method is replaced by _void_return function

                        tasks = self._add_to_event_loop(tasks,
                                                        void_result_coroutine,
                                                        end_port,
                                                        None,
                                                        edge.id,
                                                        active=False)

                    else:

                        upstream_result_copy = upstream_result.copy(deep=True)

                        # Do not trigger for None values

                        params = {end_port: upstream_result_copy.value}
                        if upstream_result_copy.value is not None:

                            # Run spec with every downstream message (param)
                            # Runs as many times as downstream edges

                            tasks = self._run_in_event_loop(tasks, node, params, end_port,
                                                            upstream_result.value, edge.id)

                        else:

                            # Missing result

                            void_result_coroutine = self._void_return(node)

                            # The original run method is replaced by _void_return function

                            tasks = self._add_to_event_loop(tasks,
                                                            void_result_coroutine,
                                                            end_port,
                                                            upstream_result.value,
                                                            edge.id,
                                                            active=False
                                                            )

        # Yield async tasks results

        for task, input_port, input_params, input_edge_id, active in tasks:

            try:
                result = await task
            except BaseException as e:
                msg = f"`{str(e)}`. Check run method of `{node.module}.{node.className}`"
                result = DagExecError(msg,
                                      port=input_port,
                                      input=input_params,
                                      edge=input_edge_id)

            yield result, input_port, input_params, input_edge_id, task_start_time, active

    @staticmethod
    def _add_results(task_results: ActionsResults, node: Node, result: Result) -> ActionsResults:
        for _, edge, _ in node.graph.out_edges:
            result_copy = result.copy(deep=True)
            task_results.add(edge.id, result_copy)
        return task_results

    @staticmethod
    async def _get_object(node: Node, params=None) -> ActionRunner:
        module = importlib.import_module(node.module)
        task_class = getattr(module, node.className)
        action = await ExecutionGraph._build(task_class, params)

        if not isinstance(action, ActionRunner):
            raise TypeError("Class {}.{} is not of type {}".format(module, node.className, type(ActionRunner)))

        return action

    @staticmethod
    async def _build(task_class, params):
        build_method = getattr(task_class, "build", None)
        if callable(build_method):
            if params:
                return await build_method(**params)
            else:
                return await build_method()

        if params:
            return task_class(**params)
        else:
            return task_class()

    async def init(self, flow, flow_history, event, session, profile) -> InitResult:
        errors = []
        objects = []
        for node in self.graph:
            # Init object
            try:
                node.object = await self._get_object(node, node.init)
                node.object.debug = self.debug
                node.object.event = event
                node.object.session = session
                node.object.profile = profile
                node.object.flow = flow
                node.object.flow_history = flow_history
                node.object.console = Console()
                node.object.id = node.id

                objects.append("{}.{}".format(node.module, node.className))
            except Exception as e:
                msg = "`{}`. This error occurred when initializing node `{}`. ".format(
                    str(e), node.id) + "Check __init__ of `{}.{}`".format(node.module, node.className)

                errors.append(msg)
                node.object = DagExecError(msg)

        return InitResult(errors=errors, objects=objects)

    @staticmethod
    def _is_result(result):
        return hasattr(result, 'port') and hasattr(result, 'value')

    def _post_process_result(self, input_port, input_params, input_edge_id, tasks_results, result,
                             node) -> ActionsResults:
        if result is not None:
            tasks_results = self._add_results(tasks_results, node, result)

        # todo remove and refactor after 15.09.2021
        # else:
        #     # Check if there are any ports bu no output
        #     if len(node.outputs) > 0:
        #         raise DagError(
        #             "Action (Node: {}) did not return Result object though there are the following output ports open {}".format(
        #                 node.id, node.outputs),
        #             port=input_port,
        #             input=input_params,
        #             edge=input_edge_id
        #         )
        #
        return tasks_results

    @staticmethod
    def _get_input_params(input_port, input_params):
        if input_port:
            return InputParams(port=input_port, value=input_params)
        return None

    async def run(self, payload, flow_id, event_id) -> DebugInfo:

        actions_results = ActionsResults()
        flow_start_time = time()
        debug_info = DebugInfo(
            timestamp=flow_start_time,
            flow=FlowDebugInfo(id=flow_id),
            event=Entity(id=event_id)
        )

        sequence_number = 0
        execution_number = 0
        for node in self.graph:  # type: Node
            task_start_time = time()
            sequence_number += 1

            node_debug_info = DebugNodeInfo(
                    id=node.id,
                    name=node.name,
                    sequenceNumber=sequence_number,
                    executionNumber=None,
                    profiler=Profiler(
                        startTime=task_start_time,
                        endTime=task_start_time,
                        runTime=task_start_time
                    ),
                )

            try:

                # Skip debug nodes when not debugging
                if not self.debug and node.debug:
                    continue

                async for result, input_port, input_params, input_edge_id, task_start_time, active in \
                        self.run_task(node, payload, ready_upstream_results=actions_results):

                    # Add information if edge is active

                    debug_info.add_debug_edge_info(input_edge_id, active)

                    # Process result

                    if isinstance(result, tuple):
                        for sub_result in result:  # type: Result
                            if self._is_result(sub_result) or sub_result is None:
                                # This is None result
                                actions_results = self._post_process_result(
                                    input_port,
                                    input_params,
                                    input_edge_id,
                                    actions_results,
                                    sub_result,
                                    node)
                            else:
                                raise DagError(
                                    "Action (Node: {}) did not return Result or tuple of Results. Expected Result got {}".format(
                                        node.id, type(result)),
                                    port=input_port,
                                    input=input_params,
                                    edge=input_edge_id
                                )
                    elif self._is_result(result) or result is None:
                        # This is None result
                        actions_results = self._post_process_result(
                            input_port,
                            input_params,
                            input_edge_id,
                            actions_results,
                            result,
                            node)
                    else:
                        # result can be DagExecError this means that this node raised exception
                        if isinstance(result, DagExecError):
                            raise DagError(
                                "Action {} raised an Exception: `{}`".format(
                                    node.className, str(result)),
                                port=input_port,
                                input=input_params,
                                edge=input_edge_id
                            )

                        raise DagError(
                            "Action (Node: {}) did not return Result or tuple of Results. Expected Result got {}".format(
                                node.id, type(result)),
                            port=input_port,
                            input=input_params,
                            edge=input_edge_id
                        )

                    # Save debug call info
                    debug_start_time = task_start_time - flow_start_time
                    debug_end_time = time() - flow_start_time
                    debug_run_time = debug_end_time - debug_start_time

                    call_debug_info = DebugCallInfo(

                        run=active,

                        profiler=Profiler(
                            startTime=debug_start_time,
                            endTime=debug_end_time,
                            runTime=debug_run_time
                        ),

                        input=DebugInput(
                            edge=Entity(id=input_edge_id) if input_edge_id is not None else None,
                            params=self._get_input_params(input_port, input_params)
                        ),
                        output=DebugOutput(
                            edge=None,  # todo
                            results=[result] if self._is_result(result) else result
                        ),

                        init=node.init,
                        profile=node.object.profile.dict() if isinstance(node.object, ActionRunner) else {},
                        console=node.object.console
                    )

                    node_debug_info.calls.append(call_debug_info)

            except (DagError, DagExecError) as e:

                debug_start_time = task_start_time - flow_start_time
                debug_end_time = time() - flow_start_time
                debug_run_time = debug_end_time - debug_start_time

                if e.input is not None and e.port is not None:

                    call_debug_info = DebugCallInfo(

                        run=True,

                        profiler=Profiler(
                            startTime=debug_start_time,
                            endTime=debug_end_time,
                            runTime=debug_run_time
                        ),
                        init=node.init,
                        input=DebugInput(
                            params=InputParams(port=e.port, value=e.input),
                            edge=Entity(id=e.edge) if e.edge is not None else None
                        ),
                        output=DebugOutput(
                            edge=None,
                            results=None
                        ),
                        profile=node.object.profile.dict() if isinstance(node.object, ActionRunner) else {},
                        error=str(e)
                    )

                else:

                    call_debug_info = DebugCallInfo(

                        run=True,

                        profiler=Profiler(
                            startTime=debug_start_time,
                            endTime=debug_end_time,
                            runTime=debug_run_time
                        ),
                        input=DebugInput(
                            edge=Entity(id=e.edge) if e.edge is not None else None,
                            params=None
                        ),
                        output=DebugOutput(
                            edge=None,
                            results=None
                        ),
                        init=node.init,
                        error=str(e),
                        profile=node.object.profile.dict() if isinstance(node.object, ActionRunner) else {},
                    )

                node_debug_info.calls.append(call_debug_info)

                # Stop workflow when there is an error
                break

            finally:
                node_debug_info.profiler.endTime = time() - flow_start_time
                node_debug_info.profiler.runTime = time() - flow_start_time - task_start_time

                # If node had call that means it was running
                if node_debug_info.calls:
                    execution_number += 1
                    node_debug_info.executionNumber = execution_number
                    debug_info.nodes[node_debug_info.id] = node_debug_info

        return debug_info

    def serialize(self):
        return self.dict()
