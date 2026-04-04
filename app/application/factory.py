from app.application.services import PipelineService


def get_pipeline_service() -> PipelineService:
    return PipelineService()
