# -*- coding: utf-8 -*-
import inspect
import sys
import typing as t
from datetime import datetime
from functools import wraps
from types import TracebackType
from uuid import uuid4

from openlineage.client import OpenLineageClient
from openlineage.client.run import Dataset
from openlineage.client.run import Job
from openlineage.client.run import Run
from openlineage.client.run import RunEvent
from openlineage.client.run import RunState


CLIENT = OpenLineageClient.from_environment()
PRODUCER = sys.argv[0]


class JobLog:
    """Context manager to send Lineage outputs."""

    def __init__(self, inputs: t.List[Dataset], outputs: t.List[Dataset], job: t.Optional[Job] = None) -> None:
        self.run = Run(str(uuid4()))
        self.job = job or Job((frame := inspect.stack()[1]).filename, frame.function)
        self.inputs = inputs
        self.outputs = outputs

    def __enter__(self) -> t.Self:
        CLIENT.emit(
            RunEvent(
                RunState.START,
                datetime.now().isoformat(),
                self.run,
                self.job,
                PRODUCER,
            ),
        )
        return self

    def __exit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_value: t.Optional[BaseException],
        exc_tb: t.Optional[TracebackType],
    ) -> None:
        CLIENT.emit(
            RunEvent(
                RunState.COMPLETE,
                datetime.now().isoformat(),
                self.run,
                self.job,
                PRODUCER,
                inputs=self.inputs,
                outputs=self.outputs,
            ),
        )


Param = t.ParamSpec("Param")
RetType = t.TypeVar("RetType")


def job_log(fn: t.Callable[Param, RetType]) -> t.Callable[Param, RetType]:

    job: t.Final = Job(namespace=fn.__module__, name=fn.__name__)

    signature = inspect.getfullargspec(fn)
    signature_0 = signature[0]

    @wraps(fn)
    def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        new_args: t.Dict[str, t.Any] = {**dict(zip(signature_0, args)), **kwargs}
        inputs = [Dataset(fn.__module__, f"{fn.__name__}/{k}") for k in new_args.keys()]
        with JobLog(job=job, inputs=inputs, outputs=[Dataset(fn.__module__, fn.__name__)]):
            return fn(*args, **kwargs)

    del signature
    return wrapper
