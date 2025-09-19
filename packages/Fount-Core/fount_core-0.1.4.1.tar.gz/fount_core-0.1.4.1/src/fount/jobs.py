from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any

class Job(ABC):

    @abstractmethod
    def status(self,_transport):
        ...

    @abstractmethod
    def metrics(self,_transport):
        ...



@dataclass
class TrainingJob(Job):
    id: str
    _transport: Any

    @classmethod
    def run(cls,_transport,job_type,payload):
        response = _transport.start_job(job_type,payload)
        return cls(id=response["id"],_transport=_transport)

    def status(self, _transport=None):
        transport = _transport or self._transport
        return transport.get_job_status(self.id)

    def metrics(self, _transport=None) :
        transport = _transport or self._transport
        return transport.get_job_metrics(self.id)


@dataclass
class TuningJob(Job):
    id: str
    _transport: Any

    @classmethod
    def run(cls,_transport,job_type,payload):
        job_id = _transport.start_job(job_type,payload)
        return cls(id=job_id,_transport=_transport)

    def status(self, _transport):
        transport = _transport or self._transport
        return transport.get_job_status(self.id)

    def metrics(self, _transport=None) :
        transport = _transport or self._transport
        return transport.get_job_metrics(self.id)


@dataclass
class InferenceJob(Job):
    id: str
    _transport: Any

    @classmethod
    def run(cls,_transport,job_type,payload):
        job_id = _transport.start_job(job_type,payload)
        return cls(id=job_id,_transport=_transport)

    def status(self, _transport):
        transport = _transport or self._transport
        return transport.get_job_status(self.id)

    def metrics(self, _transport=None) :
        transport = _transport or self._transport
        return transport.get_job_metrics(self.id)
