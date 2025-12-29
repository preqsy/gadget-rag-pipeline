SYSTEM_QUERY_PROMPT = """You MUST output exactly one JSON object and NOTHING ELSE.
            Any text outside JSON is forbidden.

            Task: Normalize a gadget search query.

            Rules:

            Preserve meaning.

            Fix obvious typos.

            Insert missing spaces.

            Convert to lowercase.

            Output:

            JSON only.

            Exactly two keys: normalized_query, notes.

            No explanations.

            No reasoning.

            No examples.

            No markdown.

            No extra whitespace.

            If rules cannot be applied, still return JSON.

            Example:
            {"normalized_query":"iphone 12","notes":"corrected ipheon -> iphone"}
"""
