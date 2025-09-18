from pydantic import BaseModel
from typing import Callable

class BaseEnvConfig(BaseModel):
    id: str     
    render_mode: str | None = None
    safe_region: dict | None = None
    scale_actions: bool = True

class BaseProjectionConfig(BaseModel):
    safe_control_fn: Callable = None
    penalty_factor: float = 0.0
