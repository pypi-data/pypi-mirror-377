from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from kreuzberg._types import LanguageDetectionConfig
from kreuzberg.exceptions import MissingDependencyError

if TYPE_CHECKING:
    from fast_langdetect import LangDetectConfig as FastLangDetectConfig

try:
    from fast_langdetect import LangDetectConfig as FastLangDetectConfig
    from fast_langdetect import detect, detect_multilingual

    HAS_FAST_LANGDETECT = True
except ImportError:  # pragma: no cover
    HAS_FAST_LANGDETECT = False
    detect = None
    detect_multilingual = None
    FastLangDetectConfig = None

_CACHE_SIZE = 128


def _create_fast_langdetect_config(config: LanguageDetectionConfig) -> FastLangDetectConfig | None:
    if not HAS_FAST_LANGDETECT or FastLangDetectConfig is None:
        return None

    kwargs: dict[str, Any] = {
        "allow_fallback": config.allow_fallback,
    }
    if config.cache_dir is not None:
        kwargs["cache_dir"] = config.cache_dir

    return FastLangDetectConfig(**kwargs)


@lru_cache(maxsize=_CACHE_SIZE)
def detect_languages(text: str, config: LanguageDetectionConfig | None = None) -> list[str] | None:
    if not HAS_FAST_LANGDETECT or detect is None or detect_multilingual is None:
        raise MissingDependencyError.create_for_package(
            dependency_group="langdetect", functionality="language detection", package_name="fast-langdetect"
        )

    if config is None:
        config = LanguageDetectionConfig()

    try:
        if config.multilingual:
            results = detect_multilingual(text, low_memory=config.low_memory, k=config.top_k)

            return [result["lang"].lower() for result in results if result.get("lang")]

        result = detect(text, low_memory=config.low_memory)
        if result and result.get("lang"):
            return [result["lang"].lower()]
        return None
    except Exception:  # noqa: BLE001
        return None
