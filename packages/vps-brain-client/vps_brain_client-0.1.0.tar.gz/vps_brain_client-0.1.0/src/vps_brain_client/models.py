from pydantic import BaseModel, Field


class ProcessTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    model: str | None = Field(
        default=None,
        description="Optional model override; defaults to configured model when omitted.",
    )
    task: str | None = Field(
        default=None,
        description="Optional task profile (e.g. sentiment, summarize, intent).",
    )


class ResponseMetadata(BaseModel):
    request_id: str
    received_at: str
    request_duration_ms: float
    inference_duration_ms: float
    prompt_chars: int
    response_chars: int


class ProcessTextResponse(BaseModel):
    status: str
    model: str
    task: str
    input_text: str
    rendered_prompt: str
    llm_response: str
    meta: ResponseMetadata
