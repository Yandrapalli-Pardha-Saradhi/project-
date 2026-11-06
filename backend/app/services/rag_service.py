from __future__ import annotations

import json
import logging
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

from app.config import Settings, SUPPORTED_LANGUAGES
from app.schemas.chat import Citation, ConversationMessage
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievedChunk, RetrievalService
from app.services.web_search_service import WebSearchResult, WebSearchService

logger = logging.getLogger("temple_heritage.rag")
_GREETING_RESPONSES = {
    "hi", "hii", "hiii", "hello", "hello there", "hi there", "hey", "hey there",
    "good morning", "good afternoon", "good evening", "namaste", "vanakkam", "namaskaram",
}
_GREETING_ANSWERS = {
    "en": "Hello! I can help you explore temples and heritage. What would you like to know?",
    "te": "నమస్కారం! ఆలయాలు, వారసత్వం గురించి తెలుసుకోవడంలో సహాయం చేస్తాను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
    "ta": "வணக்கம்! கோயில்கள் மற்றும் பாரம்பரியம் பற்றி அறிய நான் உதவுகிறேன். நீங்கள் என்ன தெரிந்துகொள்ள விரும்புகிறீர்கள்?",
    "hi": "नमस्ते! मैं मंदिरों और विरासत के बारे में जानने में मदद कर सकता हूँ। आप क्या जानना चाहेंगे?",
}
_COMPARISON = re.compile(
    r"\b(compare|comparison|versus|vs\.?|difference between|differences between|different from|differ from|"
    r"other temples|other sites|other heritage sites|different temple|across temples|across sites)\b",
    re.IGNORECASE,
)
_NAME_STOP_WORDS = {
    "temple", "temples", "group", "groups", "monument", "monuments", "complex", "at", "the", "and", "of", "site", "in",
    "what", "is", "it", "this", "that", "about", "tell", "me", "more", "which", "were", "when", "where", "who", "built",
    "architecture", "architectural", "style", "styles", "distinctive", "features", "highlighted", "with", "for", "from", "how",
    "did", "associated", "comprise", "comprises", "are", "was", "does", "do", "make", "makes", "special", "period", "dynasty",
}
_QUESTION_TOPIC_MARKERS = {
    "historical_background": ("history", "historical", "origin", "built", "construction", "dynasty", "ruler", "timeline", "century"),
    "architecture": ("architecture", "architectural", "style", "structure", "layout", "gopuram", "vimana", "mandapa", "pillar", "pillars", "sculpture", "sculptures", "carving", "carvings", "plan"),
    "religious_cultural_significance": ("deity", "deities", "worship", "religious", "sacred", "significance", "legend", "legends", "pilgrimage", "culture", "cultural"),
    "festivals_traditions": ("festival", "festivals", "ritual", "rituals", "procession", "ceremony", "ceremonies", "tradition", "traditions", "celebration"),
    "inscriptions_historical_evidence": ("inscription", "inscriptions", "epigraphy", "epigraphic", "script", "grant", "donor", "record", "records"),
    "heritage_conservation": ("heritage", "unesco", "conservation", "conserve", "restoration", "restored", "preservation", "protected", "protection", "asi"),
    "visitor_information": ("visitor", "visiting", "hours", "timings", "timing", "fee", "fees", "ticket", "tickets", "accessibility", "access", "travel", "directions"),
}
_TOPIC_METADATA_MARKERS = {
    "historical_background": ("history", "historical", "chronology", "patronage", "inscription", "epigraphy"),
    "architecture": ("architecture", "architectural", "sculpture", "construction", "plan", "engineering"),
    "religious_cultural_significance": ("religion", "religious", "deity", "worship", "culture", "significance", "tradition"),
    "festivals_traditions": ("festival", "ritual", "tradition", "culture"),
    "inscriptions_historical_evidence": ("inscription", "epigraphy", "history", "historical"),
    "heritage_conservation": ("heritage", "conservation", "preservation", "protection", "unesco"),
    "visitor_information": ("visitor", "location", "access", "tourism", "travel"),
}
_TOPIC_TEXT_EVIDENCE = {
    "historical_background": ("century", "dynasty", "ruler", "reign", "built", "construction", "historical", "commissioned", "founded", "established", "dated"),
    "architecture": ("vimana", "gopuram", "mandapa", "sanctum", "pillar", "sculpture", "carving", "architectural", "masonry", "plan"),
    "religious_cultural_significance": ("deity", "worship", "shiva", "vishnu", "buddha", "sacred", "pilgrimage", "religious", "ritual"),
    "festivals_traditions": ("festival", "ritual", "procession", "annual celebration", "ceremony", "observed during"),
    "inscriptions_historical_evidence": ("inscription", "epigraph", "inscribed", "grant", "donor record", "script"),
    "heritage_conservation": ("unesco", "conservation", "conserved", "restoration", "protected monument", "preservation", "heritage status"),
    "visitor_information": ("opening hours", "visiting hours", "entry fee", "ticket price", "visitor access", "accessibility", "visitor guidance"),
}
_HERITAGE_TERMS = re.compile(
    r"\b(temple|heritage|architecture|history|ritual|offering|prasad|pilgrimage|shrine|monument|festival|sacred|tradition)\b",
    re.IGNORECASE,
)
_CASUAL_FOOD_TERMS = re.compile(
    r"\b(idli|idly|dosa|food|meal|recipe|breakfast|lunch|dinner|snack|coffee|tea|taste|tasty)\b",
    re.IGNORECASE,
)
_CASUAL_FOOD_ANSWERS = {
    "en": "Taste is personal—there’s no single good or bad choice. I’m mainly here for temple and heritage questions, though. Want to explore a temple or tradition?",
    "te": "ఇది వ్యక్తిగత అభిరుచి—ఒకే సరైన లేదా తప్పు ఎంపిక లేదు. నేను ప్రధానంగా ఆలయాలు, వారసత్వం గురించి సహాయం చేస్తాను. ఏదైనా ఆలయం లేదా సంప్రదాయం గురించి తెలుసుకోవాలా?",
    "ta": "இது தனிப்பட்ட விருப்பம்—ஒரே சரியான அல்லது தவறான தேர்வு இல்லை. நான் முக்கியமாக கோயில்கள் மற்றும் பாரம்பரியம் பற்றி உதவுகிறேன். ஏதேனும் கோயில் அல்லது மரபைப் பற்றி அறிய விரும்புகிறீர்களா?",
    "hi": "यह व्यक्तिगत पसंद है—इसका कोई एक सही या गलत जवाब नहीं। मैं मुख्य रूप से मंदिरों और विरासत के बारे में मदद करता हूँ। क्या आप किसी मंदिर या परंपरा के बारे में जानना चाहेंगे?",
}


class RAGResult:
    def __init__(
        self,
        answer: str,
        citations: List[Citation],
        language: str,
        insufficient_evidence: bool,
        generation_disabled: bool,
        retrieved_chunks: Optional[List[RetrievedChunk]] = None,
        web_sources: Optional[List[WebSearchResult]] = None,
        context_temple_id: Optional[str] = None,
    ):
        self.answer = answer
        self.citations = citations
        self.language = language
        self.insufficient_evidence = insufficient_evidence
        self.generation_disabled = generation_disabled
        self.retrieved_chunks = retrieved_chunks or []
        self.web_sources = web_sources or []
        self.context_temple_id = context_temple_id


class RAGService:
    def __init__(
        self,
        settings: Settings,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        web_search_service: Optional[WebSearchService] = None,
    ):
        self.settings = settings
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self.web_search_service = web_search_service or WebSearchService()
        catalogue_path = Path(__file__).resolve().parents[2] / "data" / "catalogue.json"
        try:
            with catalogue_path.open("r", encoding="utf-8") as handle:
                catalogue = json.load(handle)
            self._temples = [entry for entry in catalogue if isinstance(entry, dict)] if isinstance(catalogue, list) else []
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load temple names for chat context resolution: %s", exc)
            self._temples = []
        temple_ids = {item.get("id") for item in self._temples}
        self._topic_terms: List[str] = []
        source_path = catalogue_path.parent / "raw" / "temple_sources.json"
        try:
            with source_path.open("r", encoding="utf-8") as handle:
                source_documents = json.load(handle)
            if isinstance(source_documents, list):
                self._topic_terms = sorted({
                    str(item.get("temple_id", "")).replace("_", " ").casefold()
                    for item in source_documents
                    if isinstance(item, dict)
                    and item.get("temple_id") not in temple_ids
                    and item.get("temple_id") not in {"tamil_nadu", "odisha"}
                })
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load topic names for chat context resolution: %s", exc)

    def answer_question(
        self,
        question: str,
        language: str = "en",
        temple_id: Optional[str] = None,
        history: Optional[List[ConversationMessage]] = None,
    ) -> RAGResult:
        language = (language or "en").strip()
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        history = history or []
        generation_disabled = not self.llm_service.is_enabled
        if self._is_greeting(question):
            return RAGResult(
                answer=_GREETING_ANSWERS[language],
                citations=[], language=language, insufficient_evidence=False,
                generation_disabled=False, context_temple_id=temple_id,
            )

        if self._is_simple_food_small_talk(question):
            return RAGResult(
                answer=_CASUAL_FOOD_ANSWERS[language], citations=[], language=language,
                insufficient_evidence=False, generation_disabled=False,
            )

        context_temple_id = self._resolve_temple_context(question, history, temple_id)
        temple_name = self._temple_name(context_temple_id)
        retrieval_query = question
        if context_temple_id and temple_name and temple_name.casefold() not in question.casefold():
            # Add only the resolved entity to the current turn. Prior conversation is
            # never concatenated into the vector query.
            retrieval_query = f"{question} {temple_name}"

        retrieved = self.retrieval_service.retrieve(
            retrieval_query, top_k=self.settings.top_k, temple_id=context_temple_id
        )
        if context_temple_id:
            # Keep the scope invariant even if an index adapter ignores Chroma's
            # metadata filter or returns an unexpected passage.
            retrieved = [
                chunk for chunk in retrieved
                if chunk.metadata.get("temple_id") == context_temple_id
            ]
        relevant = [chunk for chunk in retrieved if chunk.distance <= self.settings.relevance_threshold]
        relevant = self._filter_to_requested_topics(question, relevant)
        relevant = self._select_evidence(relevant, max_chunks=4)

        if not relevant:
            web_sources: List[WebSearchResult] = []
            if self.web_search_service.enabled:
                web_sources = self.web_search_service.search(retrieval_query, max_results=3)

            if not generation_disabled and web_sources:
                raw = self.llm_service.generate(
                    self._web_system_prompt(language),
                    self._web_user_prompt(question, web_sources, history),
                )
                web_ids = [f"web_{index}" for index in range(len(web_sources))]
                answer_text, cited_web_ids = self._parse_llm_output(raw, web_ids)
                cited_web_ids = list(dict.fromkeys(item for item in cited_web_ids if item in web_ids))
                answer_text = re.sub(r"\s*\[web_\d+\]", "", answer_text).strip()
                citations = self._dedupe_citations([
                    Citation(
                        source_id=f"web_{i}", source_title=result.title,
                        source_url=result.url, publisher=result.source, excerpt=result.snippet,
                    )
                    for i, result in enumerate(web_sources) if f"web_{i}" in cited_web_ids
                ])
                return RAGResult(
                    answer=answer_text, citations=citations, language=language,
                    insufficient_evidence=False, generation_disabled=False,
                    web_sources=web_sources, context_temple_id=context_temple_id,
                )

            return RAGResult(
                answer=(
                    "I couldn’t find sufficient reliable evidence in the collection to answer that. "
                    "Try asking about a temple’s history, architecture, or a specific tradition."
                ),
                citations=[], language=language, insufficient_evidence=True,
                generation_disabled=generation_disabled, context_temple_id=context_temple_id,
            )

        if generation_disabled:
            excerpts = self._retrieval_only_excerpts(relevant)
            citations = self._build_citations(excerpts)
            lines = [f'• “{self._short_excerpt(chunk.text)}”' for chunk in excerpts]
            answer = (
                "AI generation is not configured, so I can’t synthesize an answer. "
                "Relevant source excerpts:\n" + "\n".join(lines)
            )
            return RAGResult(
                answer=answer, citations=citations, language=language,
                insufficient_evidence=False, generation_disabled=True,
                retrieved_chunks=relevant, context_temple_id=context_temple_id,
            )

        raw = self.llm_service.generate(
            self._system_prompt(language, bool(context_temple_id)),
            self._user_prompt(question, relevant, history, temple_name),
        )
        retrieved_ids = [chunk.chunk_id for chunk in relevant]
        answer_text, cited_ids = self._parse_llm_output(raw, retrieved_ids)
        # The only valid citations are the passages placed in this prompt.
        allowed_ids = set(retrieved_ids)
        cited_ids = list(dict.fromkeys(chunk_id for chunk_id in cited_ids if chunk_id in allowed_ids))
        answer_text = re.sub(r"\s*\[[\w-]+_chunk_\d+\]", "", answer_text).strip()
        cited_chunks = [chunk for chunk in relevant if chunk.chunk_id in cited_ids]
        return RAGResult(
            answer=answer_text, citations=self._build_citations(cited_chunks),
            language=language, insufficient_evidence=False, generation_disabled=False,
            retrieved_chunks=relevant, context_temple_id=context_temple_id,
        )

    @staticmethod
    def _is_greeting(question: str) -> bool:
        normalized = re.sub(r"[^\w\s]", "", question.casefold()).strip()
        return normalized in _GREETING_RESPONSES

    @staticmethod
    def _is_simple_food_small_talk(question: str) -> bool:
        # Keep ordinary food opinions out of heritage retrieval. Explicit heritage
        # questions (such as temple offerings) continue through the RAG pipeline.
        return (
            len(question) <= 180
            and bool(_CASUAL_FOOD_TERMS.search(question))
            and not _HERITAGE_TERMS.search(question)
        )

    @staticmethod
    def _requested_topic_categories(question: str) -> set[str]:
        normalized = re.sub(r"[^a-z0-9]+", " ", question.casefold()).strip()
        categories = {
            category for category, markers in _QUESTION_TOPIC_MARKERS.items()
            if any(re.search(rf"\b{re.escape(marker)}\b", normalized) for marker in markers)
        }
        # "Conservation history" is a heritage/conservation topic, not a
        # request for the temple's general historical background.
        conservation_history = re.search(
            r"\b(?:conservation|preservation|restoration) history\b|"
            r"\bhistory of (?:conservation|preservation|restoration)\b",
            normalized,
        )
        other_history_markers = (
            "historical", "origin", "built", "construction", "dynasty", "ruler",
            "timeline", "century",
        )
        if conservation_history and not any(
            re.search(rf"\b{re.escape(marker)}\b", normalized) for marker in other_history_markers
        ):
            categories.discard("historical_background")
        # An explicit inscription question is historical evidence, but is kept
        # separate too so generic chronology passages cannot mask that gap.
        return categories

    @staticmethod
    def _filter_to_requested_topics(question: str, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        categories = RAGService._requested_topic_categories(question)
        if not categories:
            return chunks
        filtered: list[RetrievedChunk] = []
        for chunk in chunks:
            if any(RAGService._chunk_supports_topic(chunk, category) for category in categories):
                filtered.append(chunk)
        # For multi-topic questions, only pass evidence if every requested
        # topic has at least one supporting passage. Otherwise the chatbot
        # would be tempted to fill the missing part from unrelated context.
        if any(not any(RAGService._chunk_supports_topic(chunk, category) for chunk in filtered) for category in categories):
            return []
        return sorted(filtered, key=lambda chunk: (
            not any(RAGService._metadata_topic_matches(chunk, category) for category in categories),
            chunk.distance,
        ))

    @staticmethod
    def _chunk_supports_topic(chunk: RetrievedChunk, category: str) -> bool:
        metadata_topic = str(chunk.metadata.get("topic") or "").casefold().replace("-", "_")
        source_type = str(chunk.metadata.get("source_type") or "").casefold()
        if (
            ("inventory" in metadata_topic or "inventory" in source_type)
            and category != "visitor_information"
        ):
            # Catalogue/ASI inventory summaries establish inventory identity
            # and locality; they are not evidence for temple history, ritual,
            # architecture or conservation claims.
            return False
        text = chunk.text.casefold()
        # Metadata can help describe a passage, but it cannot by itself prove
        # that the passage contains evidence for the user's question.
        return RAGService._text_has_positive_topic_evidence(text, category)

    @staticmethod
    def _metadata_topic_matches(chunk: RetrievedChunk, category: str) -> bool:
        metadata_topic = str(chunk.metadata.get("topic") or "").casefold().replace("-", "_")
        return any(marker in metadata_topic for marker in _TOPIC_METADATA_MARKERS[category])

    @staticmethod
    def _text_has_positive_topic_evidence(text: str, category: str) -> bool:
        if category == "heritage_conservation" and re.search(
            r"\b(?:archives?|archival) index\b.{0,500}\b(?:does not reveal|does not establish|"
            r"not evidence of|cannot establish)\b.{0,140}\b(?:work|condition|protection status|"
            r"restoration|conservation)\b",
            text,
            re.IGNORECASE | re.DOTALL,
        ):
            # A catalogue/index entry whose own text explicitly says it does
            # not establish work or protection status is evidence of a record,
            # not evidence answering those heritage questions.
            return False
        if category == "inscriptions_historical_evidence":
            # A UNESCO inscription of a site is not epigraphic evidence about
            # that temple. Require wording that points to records, scripts,
            # grants, named inscriptions, or epigraphic study.
            if re.search(
                r"\b(?:no|not|without)\b[^.!?]{0,120}\b(?:epigraph|inscription)|"
                r"distinguish(?:es|ing)?\b[^.!?]{0,120}\bfrom\b[^.!?]{0,80}\b(?:epigraphic|inscriptional) evidence",
                text,
                re.IGNORECASE,
            ):
                return False
            if re.search(
                r"\b(?:epigraph(?:y|ic)|inscriptional evidence|"
                r"inscriptions?\s+(?:record|records|mention|mentions|document|documents|"
                r"attest|attests|name|names|identify|identifies|identified|list|lists|contain|contains|provide|provides)|"
                r"identified\s+in\s+inscriptions?|"
                r"(?:donor|royal|land|temple) grants?|"
                r"(?:kannada|sanskrit|tamil|telugu|grantha) script)\b",
                text,
                re.IGNORECASE,
            ):
                return True
            return False
        negative_terms = r"(?:no|not|without|does not|doesn't|do not|did not|never|unavailable|unknown|not provided|not stated|not recorded)"
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            for marker in _TOPIC_TEXT_EVIDENCE[category]:
                match = re.search(rf"\b{re.escape(marker)}\b", sentence)
                if not match:
                    continue
                before = sentence[:match.start()]
                after = sentence[match.end():]
                negative_before = re.search(rf"\b{negative_terms}\b[^.!?]{{0,180}}$", before, re.IGNORECASE)
                negative_after = re.match(rf"[^.!?]{{0,45}}\b{negative_terms}\b", after, re.IGNORECASE)
                if not negative_before and not negative_after:
                    return True
        return False

    def _resolve_temple_context(
        self,
        question: str,
        history: List[ConversationMessage],
        supplied_temple_id: Optional[str],
    ) -> Optional[str]:
        if _COMPARISON.search(question):
            return None
        current_matches = self._mentioned_temple_ids(question)
        if len(current_matches) == 1:
            return current_matches[0]
        if len(current_matches) > 1:
            return None
        normalized_question = re.sub(r"[^a-z0-9]+", " ", question.casefold())
        if any(re.search(rf"\b{re.escape(term)}\b", normalized_question) for term in self._topic_terms):
            return None
        last_assistant = next((message for message in reversed(history) if message.role == "assistant"), None)
        if last_assistant and "context_temple_id" in last_assistant.model_fields_set:
            previous_context = last_assistant.context_temple_id
            if previous_context and any(item.get("id") == previous_context for item in self._temples):
                return previous_context
            return None
        if supplied_temple_id and any(item.get("id") == supplied_temple_id for item in self._temples):
            return supplied_temple_id
        # A history-only caller still gets follow-up resolution without treating
        # the whole transcript as a search query.
        for message in reversed(history):
            if message.role == "user":
                matches = self._mentioned_temple_ids(message.content)
                if len(matches) == 1:
                    return matches[0]
        return None

    def _mentioned_temple_ids(self, text: str) -> List[str]:
        normalized = re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()
        query_tokens = [token for token in normalized.split() if token not in _NAME_STOP_WORDS]
        exact_matches: dict[str, int] = {}
        fuzzy_scores: dict[str, float] = {}
        for temple in self._temples:
            temple_id = temple.get("id")
            if not isinstance(temple_id, str):
                continue
            aliases = [temple_id, *(temple.get("names") or [])]
            for alias in aliases:
                alias_normalized = re.sub(r"[^a-z0-9]+", " ", str(alias).casefold()).strip()
                alias_tokens = [token for token in alias_normalized.split() if token not in _NAME_STOP_WORDS]
                # Generic catalogue labels like "Temple" cannot identify an
                # entity; do not let them capture unrelated questions.
                if not alias_tokens:
                    continue
                if alias_normalized and re.search(rf"\b{re.escape(alias_normalized)}\b", normalized):
                    # Prefer the most specific full catalogue name when it
                    # contains a shared short alias (for example
                    # "Sivadol (Gaurisagar)" vs "Sivadol (Joysagar)").
                    # A query containing only the shared alias still remains
                    # ambiguous, which is safer than guessing.
                    exact_matches[temple_id] = max(
                        exact_matches.get(temple_id, 0), len(alias_normalized)
                    )
                for query_token in query_tokens:
                    for alias_token in alias_tokens:
                        # A single short token is too weak to identify a temple
                        # (and generic follow-up words can collide with names).
                        # Full alias matches above still resolve short names.
                        if query_token == alias_token and len(query_token) >= 8:
                            fuzzy_scores[temple_id] = max(fuzzy_scores.get(temple_id, 0.0), 1.0)
                        # Fuzzy aliases are useful for long transliteration typos,
                        # but short everyday words (for example "layout") can
                        # accidentally resemble a temple-name token and erase the
                        # conversation's selected-temple scope. Restrict fuzzy
                        # matching to long, near-equal-length tokens.
                        elif (
                            min(len(query_token), len(alias_token)) >= 8
                            and abs(len(query_token) - len(alias_token)) <= 2
                        ):
                            ratio = SequenceMatcher(None, query_token, alias_token).ratio()
                            if ratio >= 0.88:
                                fuzzy_scores[temple_id] = max(fuzzy_scores.get(temple_id, 0.0), ratio)
        if exact_matches:
            longest_match = max(exact_matches.values())
            return [
                temple_id for temple_id, match_length in exact_matches.items()
                if match_length == longest_match
            ]
        if not fuzzy_scores:
            return []
        highest = max(fuzzy_scores.values())
        return [temple_id for temple_id, score in fuzzy_scores.items() if abs(score - highest) < 0.015]

    def _temple_name(self, temple_id: Optional[str]) -> Optional[str]:
        for temple in self._temples:
            if temple.get("id") == temple_id:
                names = temple.get("names") or []
                return names[0] if names else temple_id
        return None

    @staticmethod
    def _select_evidence(chunks: List[RetrievedChunk], max_chunks: int) -> List[RetrievedChunk]:
        selected: List[RetrievedChunk] = []
        seen_documents: set[str] = set()
        for chunk in chunks:
            document_id = str(chunk.metadata.get("document_id") or chunk.chunk_id)
            if document_id not in seen_documents:
                selected.append(chunk)
                seen_documents.add(document_id)
                if len(selected) == max_chunks:
                    return selected
        for chunk in chunks:
            if chunk not in selected:
                selected.append(chunk)
                if len(selected) == max_chunks:
                    break
        return selected

    @staticmethod
    def _retrieval_only_excerpts(chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        selected: List[RetrievedChunk] = []
        seen: set[str] = set()
        for chunk in chunks:
            source = str(chunk.metadata.get("source_url") or chunk.metadata.get("document_id") or chunk.chunk_id)
            if source in seen:
                continue
            seen.add(source)
            selected.append(RetrievedChunk(chunk.chunk_id, RAGService._short_excerpt(chunk.text), chunk.distance, chunk.metadata))
            if len(selected) == 2:
                break
        return selected

    @staticmethod
    def _short_excerpt(text: str, limit: int = 220) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        limitation = next((sentence for sentence in sentences if re.search(
            r"\b(does not state|does not specify|not specified|not provided|remain unknown|insufficient information)\b",
            sentence,
            re.IGNORECASE,
        )), None)
        # Keep explicit evidence limits visible in retrieval-only mode. Returning
        # only the opening inventory sentence could otherwise make it look like
        # the source supported a historical claim it actually says is unknown.
        first_sentence = limitation or (sentences[0] if sentences else "")
        if len(first_sentence) <= limit:
            return first_sentence
        return first_sentence[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"

    def _system_prompt(self, language: str, temple_scoped: bool = False) -> str:
        scope_instruction = (
            "Stay focused on the one temple identified in the question or conversation. Do not introduce other temples unless the user asks for a comparison. "
            if temple_scoped else
            "Do not introduce unrelated temples; mention multiple sites only when the question asks about them. "
        )
        return (
            "You are a careful assistant answering questions about Indian temples and heritage sites. "
            f"Answer ONLY in the user's requested language: {language}. "
            "Use ONLY the evidence passages provided; never add outside facts. "
            + scope_instruction
            + "Answer the current question directly in at most three concise sentences. Do not repeat or dump the source passages. "
            "Use conversation history only to resolve references such as 'this temple' or 'tell me more'; it is not evidence. "
            "If the evidence does not support the requested detail, briefly say what is missing. "
            'Return one JSON object only with keys "answer" and "cited_chunk_ids". '
            "Put supporting retrieved chunk IDs only in cited_chunk_ids; do not print raw IDs in the answer. "
            "Never invent URLs, source titles, chunk IDs, or facts."
        )

    def _user_prompt(
        self,
        question: str,
        relevant: List[RetrievedChunk],
        history: List[ConversationMessage],
        temple_name: Optional[str],
    ) -> str:
        lines = []
        for index, chunk in enumerate(relevant, start=1):
            lines.append(
                f"[{index}] Chunk ID: {chunk.chunk_id}\n"
                f"Source: {chunk.metadata.get('source_title', 'unknown source')}\n"
                f"Text: {chunk.text}"
            )
        recent_history = history[-8:]
        history_text = "\n".join(f"{message.role.title()}: {message.content}" for message in recent_history)
        context_line = f"Resolved temple context: {temple_name}\n" if temple_name else ""
        history_block = f"Recent conversation (reference context only):\n{history_text}\n\n" if history_text else ""
        return (
            f"{context_line}{history_block}Evidence passages:\n" + "\n\n".join(lines)
            + f"\n\nCurrent question: {question}\n\nProduce the concise JSON response."
        )

    @staticmethod
    def _web_system_prompt(language: str) -> str:
        return (
            f"Answer only in {language}, using only the supplied web snippets. Be concise, "
            "state uncertainty when snippets do not support a detail, and return JSON with "
            'keys "answer" and "cited_chunk_ids". Cite only supplied web reference IDs actually used.'
        )

    @staticmethod
    def _web_user_prompt(question: str, sources: List[WebSearchResult], history: List[ConversationMessage]) -> str:
        context = "\n".join(f"{message.role}: {message.content}" for message in history[-8:])
        evidence = "\n".join(
            f"Reference ID: web_{index}\nTitle: {item.title}\nURL: {item.url}\nSnippet: {item.snippet}"
            for index, item in enumerate(sources)
        )
        return f"Conversation context:\n{context}\n\nWeb snippets:\n{evidence}\n\nQuestion: {question}"

    @staticmethod
    def _parse_llm_output(raw: str, retrieved_ids: List[str]) -> Tuple[str, List[str]]:
        text = raw.strip()
        answer = text
        cited: List[str] = []
        cleaned = re.sub(r"```json|```", "", text).strip()
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                answer = str(data.get("answer", text))
                ids = data.get("cited_chunk_ids", [])
                if isinstance(ids, list):
                    cited = [str(chunk_id) for chunk_id in ids]
        except (json.JSONDecodeError, ValueError):
            cited = [chunk_id for chunk_id in retrieved_ids if chunk_id in text]
        return answer, cited

    @staticmethod
    def _build_citations(chunks: List[RetrievedChunk]) -> List[Citation]:
        citations: List[Citation] = []
        for chunk in chunks:
            metadata = chunk.metadata or {}
            source_id = metadata.get("document_id") or chunk.chunk_id.rsplit("_chunk_", 1)[0]
            source_url = metadata.get("source_url", "")
            citations.append(Citation(
                source_id=source_id,
                source_title=metadata.get("source_title", "Unknown title"),
                source_url=source_url,
                publisher=metadata.get("publisher") or None,
                excerpt=chunk.text,
            ))
        return RAGService._dedupe_citations(citations)

    @staticmethod
    def _dedupe_citations(citations: List[Citation]) -> List[Citation]:
        unique: List[Citation] = []
        seen: set[str] = set()
        for citation in citations:
            if citation.source_url:
                parsed = urlsplit(citation.source_url)
                key = urlunsplit((parsed.scheme.casefold(), parsed.netloc.casefold(), parsed.path.rstrip("/") or "/", parsed.query, parsed.fragment))
            else:
                key = citation.source_id
            if key in seen:
                continue
            seen.add(key)
            unique.append(citation)
        return unique
