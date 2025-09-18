from typing import Optional

from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.pipe_abstract import PipeAbstract
from pipelex.core.pipes.pipe_run_params import PipeRunParams
from pipelex.core.pipes.pipe_run_params_factory import PipeRunParamsFactory
from pipelex.pipe_works.pipe_job import PipeJob
from pipelex.pipeline.job_metadata import JobMetadata


class PipeJobFactory:
    @classmethod
    def make_pipe_job(
        cls,
        pipe: PipeAbstract,
        pipe_run_params: Optional[PipeRunParams] = None,
        working_memory: Optional[WorkingMemory] = None,
        job_metadata: Optional[JobMetadata] = None,
        output_name: Optional[str] = None,
    ) -> PipeJob:
        job_metadata = job_metadata or JobMetadata()
        working_memory = working_memory or WorkingMemoryFactory.make_empty()
        if not pipe_run_params:
            pipe_run_params = PipeRunParamsFactory.make_run_params()
        return PipeJob(
            job_metadata=job_metadata,
            working_memory=working_memory,
            pipe_run_params=pipe_run_params,
            pipe=pipe,
            output_name=output_name,
        )
