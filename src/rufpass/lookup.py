"""Best-effort exact phone lookup in Wikidata's freely reusable structured data."""

import json
import logging
import re
import time
import unicodedata
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LOG = logging.getLogger("rufpass")


class NameLookup:
    def __init__(self):
        self.next_request = 0

    def find(self, number):
        if re.fullmatch(r"\+[1-9][0-9]{6,14}", number) is None:
            return None
        now = time.monotonic()
        if now < self.next_request:
            return None
        self.next_request = now + 1
        digits = number[1:]
        query = '''SELECT ?item ?itemLabel (SAMPLE(?value) AS ?phone) WHERE {
            ?item wdt:P1329 ?value .
            FILTER(REPLACE(STR(?value), "[^0-9]", "") IN ("%s", "00%s"))
            FILTER NOT EXISTS { ?item wdt:P31 wd:Q5 }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en". }
        } GROUP BY ?item ?itemLabel LIMIT 2''' % (digits, digits)
        request = Request("https://query.wikidata.org/sparql?" + urlencode({"query": query}), headers={
            "User-Agent": "Rufpass/0.2.3 (https://github.com/maxglas/Rufpass)",
            "Accept": "application/sparql-results+json",
        })
        try:
            with urlopen(request, timeout=3) as response:
                body = response.read(65537)
            if len(body) > 65536:
                raise ValueError("Response too large")
            rows = json.loads(body)["results"]["bindings"]
            owners = {}
            for row in rows:
                phone = row["phone"]["value"]
                if not re.fullmatch(r"(?:\+|00)[0-9 ()/.-]+", phone):
                    continue
                actual = re.sub(r"[^0-9]", "", phone).removeprefix("00")
                if actual != digits:
                    continue
                item = row["item"]["value"]
                name = row["itemLabel"]["value"]
                if not re.fullmatch(r"https?://www.wikidata.org/entity/Q[0-9]+", item):
                    continue
                if not name.strip() or re.fullmatch(r"Q[0-9]+", name.strip()):
                    return None
                if any(unicodedata.category(char).startswith("C") for char in name):
                    return None
                owners[item] = " ".join(name.split())[:80]
            return next(iter(owners.values())) if len(owners) == 1 else None
        except HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After", "60")
                seconds = int(retry_after) if retry_after.isascii() and retry_after.isdecimal() else 60
                self.next_request = time.monotonic() + min(max(seconds, 60), 3600)
            LOG.warning("Namenssuche nicht verfügbar (HTTP %s); Name unbekannt wird verwendet.", exc.code)
        except Exception as exc:
            # Exception text can contain the query URL and the dialled number.
            LOG.warning("Namenssuche fehlgeschlagen (%s); Name unbekannt wird verwendet.", type(exc).__name__)
        return None
