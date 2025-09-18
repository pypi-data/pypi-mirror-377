from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep

PipelineSteps = BasePipelineStep | list[BasePipelineStep]
