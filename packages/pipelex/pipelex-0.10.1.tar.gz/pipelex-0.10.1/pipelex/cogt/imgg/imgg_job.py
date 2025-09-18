from datetime import datetime

from typing_extensions import override

from pipelex.cogt.imgg.imgg_engine import ImggEngine
from pipelex.cogt.imgg.imgg_job_components import ImggJobConfig, ImggJobParams, ImggJobReport
from pipelex.cogt.imgg.imgg_prompt import ImggPrompt
from pipelex.cogt.inference.inference_job_abstract import InferenceJobAbstract


class ImggJob(InferenceJobAbstract):
    imgg_prompt: ImggPrompt
    job_params: ImggJobParams
    job_config: ImggJobConfig
    job_report: ImggJobReport

    @override
    def validate_before_execution(self):
        self.imgg_prompt.validate_before_execution()

    def imgg_job_before_start(self, imgg_engine: ImggEngine):
        # Reset metadata
        self.job_metadata.started_at = datetime.now()

        # Reset outputs
        self.job_report = ImggJobReport()

    def imgg_job_after_complete(self):
        self.job_metadata.completed_at = datetime.now()
