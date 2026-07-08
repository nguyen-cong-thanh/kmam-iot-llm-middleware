"""LangChain integration: build chat models and wire the LLM tier of the detector.

A small factory hides the two backends used in the experiment behind a single
interface (report section 3.3.1): ``deepseek-v4-flash`` reached through the DeepSeek API
and ``gemma-4-E2B`` running locally through Ollama. The rest of the system depends only
on an object exposing ``invoke``, so the choice of model stays isolated here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from kmam.context import Verdict
from kmam.detection.detector import PromptInjectionDetector
from kmam.detection.llm_classifier import LLMClassifier
from kmam.detection.rules import RuleFilter


@dataclass(frozen=True)
class ModelConfig:
    """A named LLM configuration used in the experiment."""

    name: str
    backend: str
    model: str


# The two models compared in Chapter III (report section 3.3.1).
MODEL_REGISTRY: dict[str, ModelConfig] = {
    "deepseek": ModelConfig("deepseek", "deepseek-api", "deepseek-v4-flash"),
    "gemma": ModelConfig("gemma", "ollama-local", "gemma4:e2b"),
}


def build_chat_model(backend: str, model: str, temperature: float = 0.0):
    """Instantiate a LangChain chat model for the given backend.

    ``temperature`` defaults to 0 so runs are as reproducible as the model allows.
    """
    load_dotenv()
    if backend == "deepseek-api":
        from langchain_deepseek import ChatDeepSeek

        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set (expected in .env)")
        # deepseek-v4-flash defaults to "thinking" mode, which rejects the tool_choice
        # used by structured output. Disable thinking so the classification task (a
        # simple binary decision) can use structured output and runs faster.
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            api_key=api_key,
            extra_body={"thinking": {"type": "disabled"}},
        )
    if backend == "ollama-local":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=model, temperature=temperature)
    raise ValueError(f"unknown backend: {backend}")


def build_model_by_name(name: str, temperature: float = 0.0):
    """Instantiate a chat model from the :data:`MODEL_REGISTRY`."""
    config = MODEL_REGISTRY[name]
    return build_chat_model(config.backend, config.model, temperature)


def build_llm_detector(
    name: str,
    temperature: float = 0.0,
    uncertain_default: Verdict = Verdict.ALLOW,
) -> PromptInjectionDetector:
    """Build a two-tier detector whose LLM tier is backed by the named model."""
    chat_model = build_model_by_name(name, temperature)
    return PromptInjectionDetector(
        rule_filter=RuleFilter(),
        llm_classifier=LLMClassifier(chat_model),
        uncertain_default=uncertain_default,
    )
