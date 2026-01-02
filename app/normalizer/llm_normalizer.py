from __future__ import annotations
from dataclasses import dataclass
import logging
import json
import re
from typing import Any, Dict, Optional, Tuple
from llama_index.llms.ollama import Ollama

from prompts import SYSTEM_QUERY_PROMPT


@dataclass(frozen=True)
class NormalizationResult:
    raw_query: str
    normalized_query: str
    notes: Optional[str] = None
    used_llm: bool = False


logger = logging.getLogger(__name__)


class LLMQueryNormalizer:
    SYSTEM_PROMPT = SYSTEM_QUERY_PROMPT

    def __init__(
        self,
        model: str = "llama3.2:3b",
        # model: str = "qwen2.5:7b",
        temperature: float = 0.0,
    ) -> None:
        self.llm = Ollama(
            model=model,
            temperature=temperature,
            request_timeout=60.0,
            additional_kwargs={"num_ctx": 2048, "num_predict": 128},
        )
        logger.info(f"Starting LLM service with model: {model}")

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        If model accidentally adds text, try to extract JSON object.
        """
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)

        if not m:
            raise ValueError("No JSON object found in LLM output")
        return m.group(0)

    @staticmethod
    def _validate(obj: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Hard validation to keep behaviour safe and determinstic
        """

        required_keys = {
            "normalized_query",
            "notes",
        }
        if set(obj.keys()) != required_keys:
            return (
                False,
                f"Invalid keys. Expected {required_keys}, got {set(obj.keys())}",
            )

        if (
            not isinstance(obj["normalized_query"], str)
            or not obj["normalized_query"].strip()
        ):
            return False, "normalized_query must be non-empty string"

        nq = " ".join(obj["normalized_query"].strip().lower().split())
        obj["normalized_query"] = nq

        return True, ""

    def normalize(self, query: str) -> NormalizationResult:
        raw = query
        prompt = f"""Normalize this gadget query strictly as JSON to match the real life name(Nigerian gadgets).  
        Return only a single JSON object with exactly two keys: "normalized_query" and "notes".  
        Do not output anything else, no explanations, no markdown, no extra text and MAKE SURE THE normalized_query IS A GADGET.  

Query: "{raw}" """

        resp = self.llm.complete(
            system_prompt=self.SYSTEM_PROMPT,
            prompt=prompt,
        ).text

        try:
            json_text = self._extract_json(resp)
            obj = json.loads(json_text)

            ok, err = self._validate(obj)
            if not ok:
                raise ValueError(err)

            return NormalizationResult(
                raw_query=raw,
                normalized_query=obj["normalized_query"],
                notes=obj["notes"],
                used_llm=True,
            )
        except Exception:
            return NormalizationResult(
                raw_query=raw,
                normalized_query=" ".join(raw.strip().lower().split()),
                used_llm=False,
                notes="LLM normalization failed; fallback to basic lowercase normalization",
            )
