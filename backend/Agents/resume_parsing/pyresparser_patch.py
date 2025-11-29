"""Compatibility helpers for running pyresparser with spaCy>=3."""

from __future__ import annotations

import io
import os
from typing import Optional

import spacy
from spacy.matcher import Matcher

from pyresparser import utils
from pyresparser import resume_parser as _resume_parser


class _CompatMatcher(Matcher):
    """Matcher that accepts the legacy spaCy v2 add() calling convention."""

    def add(self, key, on_match=None, *patterns, **kwargs):  # type: ignore[override]
        greedy = kwargs.pop("greedy", "LONGEST")
        callback_kw = kwargs.pop("on_match", None)
        if kwargs:
            # spaCy's Matcher.add doesn't accept other kwargs, keep parity
            raise TypeError("Unexpected keyword arguments: %s" % ", ".join(kwargs))

        # spaCy v2 style: matcher.add(key, on_match, *patterns)
        if patterns and (callable(on_match) or on_match is None):
            callback = on_match
            pattern_list = list(patterns)
        else:
            # spaCy v3 style: matcher.add(key, patterns, on_match=callback)
            pattern_list = on_match
            if pattern_list is None:
                pattern_list = []
            elif not isinstance(pattern_list, list):
                pattern_list = [pattern_list]
            else:
                pattern_list = list(pattern_list)
            extra = list(patterns)
            callback = callback_kw
            if extra and callable(extra[-1]) and callback is None:
                callback = extra.pop()
            if extra:
                pattern_list.extend(extra)

        if not pattern_list:
            raise ValueError("Expected at least one pattern for Matcher.add")

        try:
            self.remove(key)
        except (KeyError, ValueError):
            pass
        return super().add(key, pattern_list, on_match=callback, greedy=greedy)


def _patched_init(
    self,
    resume,
    skills_file: Optional[str] = None,
    custom_regex: Optional[str] = None,
) -> None:
    """Drop-in replacement for ResumeParser.__init__ with graceful fallback."""
    nlp = spacy.load("en_core_web_sm")
    try:
        custom_model_path = os.path.dirname(os.path.abspath(_resume_parser.__file__))
        custom_nlp = spacy.load(custom_model_path)
    except OSError:
        # pyresparser ships a spaCy v2 model that spaCy>=3.0 cannot load.
        # Fall back to the generic English model so the object still works.
        custom_nlp = nlp

    # set mangled attributes expected by original class implementation
    if isinstance(resume, os.PathLike):
        resume = os.fspath(resume)

    self._ResumeParser__skills_file = skills_file
    self._ResumeParser__custom_regex = custom_regex
    self._ResumeParser__matcher = _CompatMatcher(nlp.vocab)
    self._ResumeParser__details = {
        "name": None,
        "email": None,
        "mobile_number": None,
        "skills": None,
        "college_name": None,
        "degree": None,
        "designation": None,
        "experience": None,
        "company_names": None,
        "no_of_pages": None,
        "total_experience": None,
    }
    self._ResumeParser__resume = resume
    if not isinstance(self._ResumeParser__resume, io.BytesIO):
        ext = os.path.splitext(self._ResumeParser__resume)[1].split(".")[1]
    else:
        ext = self._ResumeParser__resume.name.split(".")[1]
    self._ResumeParser__text_raw = utils.extract_text(self._ResumeParser__resume, "." + ext)
    self._ResumeParser__text = " ".join(self._ResumeParser__text_raw.split())
    self._ResumeParser__nlp = nlp(self._ResumeParser__text)
    self._ResumeParser__custom_nlp = custom_nlp(self._ResumeParser__text_raw)
    self._ResumeParser__noun_chunks = list(self._ResumeParser__nlp.noun_chunks)
    # call original helper using name-mangled reference
    _resume_parser.ResumeParser._ResumeParser__get_basic_details(self)


def apply_pyresparser_patch() -> None:
    """Apply the patched constructor exactly once."""
    if _resume_parser.ResumeParser.__init__ is not _patched_init:
        _resume_parser.ResumeParser.__init__ = _patched_init
