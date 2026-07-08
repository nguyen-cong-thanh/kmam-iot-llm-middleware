"""LangChain integration: build chat models and wire the LLM tier of the detector.

A small factory hides the LLM backend used in the experiment behind a single
interface (report section 3.3.1): ``deepseek-v4-flash`` reached through the DeepSeek API.
The rest of the system depends only on an object exposing ``invoke``, so the choice of
model stays isolated here and a different backend can be added without touching callers.
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


# The LLM tier backend used in Chapter III (report section 3.3.1).
MODEL_REGISTRY: dict[str, ModelConfig] = {
    "deepseek": ModelConfig("deepseek", "deepseek-api", "deepseek-v4-flash"),
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
    raise ValueError(f"unknown backend: {backend}")


def build_model_by_name(name: str, temperature: float = 0.0):
    """Instantiate a chat model from the :data:`MODEL_REGISTRY`."""
    config = MODEL_REGISTRY[name]
    return build_chat_model(config.backend, config.model, temperature)


def build_llm_detector(
    name: str,
    temperature: float = 0.0,
    uncertain_default: Verdict = Verdict.ALLOW,
    escalate_all: bool = False,
) -> PromptInjectionDetector:
    """Build a two-tier detector whose LLM tier is backed by the named model.

    ``escalate_all`` selects the escalation strategy (approach A vs B, see
    :class:`~kmam.detection.detector.PromptInjectionDetector`).
    """
    chat_model = build_model_by_name(name, temperature)
    return PromptInjectionDetector(
        rule_filter=RuleFilter(),
        llm_classifier=LLMClassifier(chat_model),
        uncertain_default=uncertain_default,
        escalate_all=escalate_all,
    )
