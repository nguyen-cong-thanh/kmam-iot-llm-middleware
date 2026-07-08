"""LangChain integration for the experiment (chat models and the LLM detector tier)."""

from kmam.agent.langchain_integration import (
    MODEL_REGISTRY,
    ModelConfig,
    build_chat_model,
    build_llm_detector,
    build_model_by_name,
)

__all__ = [
    "MODEL_REGISTRY",
    "ModelConfig",
    "build_chat_model",
    "build_llm_detector",
    "build_model_by_name",
]
