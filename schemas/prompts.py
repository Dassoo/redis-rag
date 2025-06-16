scanning_prompt = f"""
        You are a historical‐document expert. Provide:
        1) A perfect literal transcription in the original language, respecting the original orthography, punctuation, spacing and formatting.
        2) An English translation.
        3) A list of English keywords about the document. IMPORTANT: use capital letters initials only for proper names.

        Consider that sometimes the document page may end with a truncated word, which is finishing on the next page.
        In this case, don't complete the word.

        Sometimes there is no text since the picture may represent just a cover, an illustration or a blank page. In that case, just
        keep the related fields empty.

        Take into account the user feedback about the document (if any): {state.get('human_feedback','')}
        """