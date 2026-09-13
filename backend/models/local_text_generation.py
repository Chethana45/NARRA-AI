"""
Local, fully-offline story generation fallback (used only when GEMINI_API_KEY
is not configured). Heavy deps (torch/transformers) are imported lazily.
"""


class TextGenerationModel:
    def __init__(self, device: str = "cpu") -> None:
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        except ImportError as exc:
            raise RuntimeError(
                "Local fallback story generation requires 'torch' and 'transformers'. "
                "Install them with: pip install -r requirements-local.txt"
            ) from exc

        self._torch = torch
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base").to(self.device)
        self.model.eval()

    def generate_story(self, caption: str, style: str, facts: list[str] | None = None, user_context: str | None = None) -> str:
        # Instruction-style prompt tailored for FLAN-T5. Keep this function focused on prompting and retry logic.
        style_map = {
            "Natural": "realistic and warm",
            "Funny": "humorous and playful",
            "Cinematic": "cinematic and dramatic",
            "Emotional": "emotional and heartfelt",
            "Informative": "clear, polished and descriptive",
            "Inspirational": "uplifting and inspiring",
            "Mysterious": "mysterious and intriguing",
            # legacy aliases kept for backward compatibility
            "Professional": "clear, polished and descriptive",
            "Storytelling": "cinematic and dramatic",
        }
        style_instruction = style_map.get(style, "engaging")

        # FLAN-T5-base is small and prone to hallucinating specifics, so we
        # deliberately keep any researched facts out of its free-form prompt
        # and only ever mention that verified context exists generically --
        # this avoids it inventing wrong dates/numbers around a real fact.
        context_note = ""
        if user_context and facts:
            context_note = (
                f" The scene is associated with '{user_context}'; keep the tone "
                "respectful and grounded rather than inventing specific biographical claims."
            )
        elif user_context:
            context_note = f" The scene is associated with '{user_context}'."

        # Normalize caption: collapse obvious repeated phrases like "X and X" or duplicate tokens
        import re
        normalized_caption = caption or ""
        # replace exact repeated phrase '... and ...' where both sides match
        m = re.search(r"\b(.+?)\b\s+and\s+\1\b", normalized_caption, flags=re.IGNORECASE)
        if m:
            normalized_caption = re.sub(m.group(0), m.group(1), normalized_caption, flags=re.IGNORECASE)
        # collapse repeated words
        normalized_caption = re.sub(r"\b(\w+)\s+\1\b", r"\1", normalized_caption, flags=re.IGNORECASE)
        normalized_caption = normalized_caption.strip()

        # Helper to log required debug info to terminal
        def log_debug(label: str, text: str) -> None:
            try:
                print(f"{label}: {text}")
            except Exception:
                pass

        # Generate with controlled decoding parameters
        def run_generate(prompt: str, gen_kwargs: dict) -> str:
            log_debug("STORY PROMPT", prompt)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with self._torch.no_grad():
                try:
                    outputs = self.model.generate(**inputs, **gen_kwargs)
                except TypeError:
                    # fallback for older transformers that don't accept min_new_tokens / max_new_tokens
                    fallback_kwargs = gen_kwargs.copy()
                    if "max_new_tokens" in fallback_kwargs:
                        fallback_kwargs.pop("max_new_tokens")
                    if "min_new_tokens" in fallback_kwargs:
                        fallback_kwargs.pop("min_new_tokens")
                    outputs = self.model.generate(**inputs, **fallback_kwargs)
            raw = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            log_debug("RAW MODEL OUTPUT", raw)
            # Strip any prompt echo if present
            cleaned = raw
            if prompt.strip() and prompt.strip() in cleaned:
                cleaned = cleaned.replace(prompt.strip(), "").strip()
            # additionally remove repeated caption occurrences
            if normalized_caption and normalized_caption.strip() in cleaned:
                cleaned = cleaned.replace(normalized_caption.strip(), "").strip()
            return cleaned

        # Primary generation attempt uses a two-step approach to avoid parroting the caption
        gen_kwargs = {
            "max_new_tokens": 120,
            "min_new_tokens": 60,
            "num_beams": 4,
            "no_repeat_ngram_size": 3,
            "repetition_penalty": 1.2,
            "early_stopping": True,
            "do_sample": False,
        }

        # Log caption
        log_debug("CAPTION", caption)

        # Step 1: generate a short paraphrased seed that avoids using exact phrases
        seed_prompt = (
            "Paraphrase the scene in 10-15 words without repeating exact phrases from the scene.\n"
            f"Scene: {normalized_caption}\n\nParaphrase:"
        )
        seed_kwargs = {"max_new_tokens": 30, "do_sample": True, "top_p": 0.9, "temperature": 0.9, "num_beams": 4, "no_repeat_ngram_size": 2, "repetition_penalty": 1.1}
        seed = run_generate(seed_prompt, seed_kwargs).strip()
        log_debug("SEED", seed)
        # If seed is empty or too similar to caption, fall back to using normalized_caption as seed
        def similar(a: str, b: str) -> bool:
            if not a or not b:
                return False
            la = set(a.lower().split())
            lb = set(b.lower().split())
            overlap = len(la.intersection(lb)) / max(1, len(lb))
            return overlap > 0.7

        if not seed or similar(seed, normalized_caption):
            seed = normalized_caption

        # Step 2: expand the seed into a story
        expand_prompt = (
            "Write a creative short story of about 80-120 words based on the following seed.\n"
            "Do not repeat the original scene text or paraphrase it directly.\n\n"
            f"Seed: {seed}{context_note}\n\n"
            f"Style: {style_instruction}\n\nStory:"
        )
        story = run_generate(expand_prompt, gen_kwargs).strip()

        # Helper to judge quality
        def is_too_similar_or_short(s: str) -> bool:
            if not s:
                return True
            words = s.split()
            if len(words) < 40:
                return True
            low_s = " ".join(words).lower()
            low_c = (normalized_caption or "").lower().strip()
            if not low_c:
                return False
            # basic containment check
            if low_c in low_s or low_s in low_c:
                return True
            # word overlap ratio
            s_words = set([w.strip(".,!?;:\"'()[]") for w in low_s.split() if w])
            c_words = set([w.strip(".,!?;:\"'()[]") for w in low_c.split() if w])
            if c_words:
                overlap = len(s_words.intersection(c_words)) / max(1, len(c_words))
                if overlap > 0.6:
                    return True
            return False

        # If primary output is bad, retry once with a simpler expansion instruction and sampling
        if is_too_similar_or_short(story):
            retry_prompt = (
                "Expand the following scene into a short creative story (~80-120 words).\n"
                "Do not repeat the scene text; add atmosphere and a small narrative arc. Avoid violence and explicit content.\n\n"
                f"Scene: {normalized_caption}{context_note}\n\n"
                f"Style: {style_instruction}\n\n"
                "Story:"
            )
            retry_kwargs = {
                "max_new_tokens": 140,
                "min_new_tokens": 60,
                "num_beams": 4,
                "no_repeat_ngram_size": 3,
                "repetition_penalty": 1.2,
                "early_stopping": True,
                "do_sample": True,
                "top_p": 0.95,
                "temperature": 0.9,
            }
            retry_story = run_generate(retry_prompt, retry_kwargs).strip()
            log_debug("RAW MODEL OUTPUT (RETRY)", retry_story)
            # If retry is better, use it
            if not is_too_similar_or_short(retry_story):
                story = retry_story
            else:
                # If retry produced violent content or repeated caption, attempt a safety regeneration forbidding people/violence
                lower_retry = retry_story.lower()
                blacklist = ["kill", "murder", "rape", "gun", "blood", "stab", "die", "attack"]
                if any(b in lower_retry for b in blacklist) or is_too_similar_or_short(retry_story):
                    safe_prompt = (
                        "Create a calm, non-violent atmospheric vignette of about 80-120 words inspired by the scene.\n"
                        "Do NOT mention people, harm, violence, or graphic events. Focus on light, color, objects, and mood suggested by the image.\n\n"
                        f"Scene: {normalized_caption}\n\n"
                        f"Style: {style_instruction}\n\n"
                        "Story:"
                    )
                    safe_kwargs = {
                        "max_new_tokens": 140,
                        "min_new_tokens": 60,
                        "num_beams": 5,
                        "no_repeat_ngram_size": 3,
                        "repetition_penalty": 1.2,
                        "early_stopping": True,
                        "do_sample": False,
                    }
                    safe_story = run_generate(safe_prompt, safe_kwargs).strip()
                    log_debug("RAW MODEL OUTPUT (SAFETY)", safe_story)
                    if not is_too_similar_or_short(safe_story):
                        story = safe_story

        # Final safety: if still unacceptable, do not return caption or short repetition
        if is_too_similar_or_short(story):
            log_debug("FINAL STORY", "<generation failed quality checks; returning empty story>")
            print(f"FINAL STORY: {''}")
            return ""

        log_debug("FINAL STORY", story)
        return story.strip()
