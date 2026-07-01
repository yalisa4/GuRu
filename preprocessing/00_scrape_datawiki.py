# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beautifulsoup4==4.13.4",
#     "requests==2.32.5",
# ]
# ///

import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import requests
    from bs4 import BeautifulSoup
    import re
    from dataclasses import dataclass, field, asdict
    from typing import Optional, ClassVar
    import pandas as pd

    from pathlib import Path
    from datetime import date
    return (
        BeautifulSoup,
        ClassVar,
        Optional,
        Path,
        asdict,
        dataclass,
        date,
        pd,
        re,
        requests,
    )


@app.cell
def _(Path, date):
    # ── Constants ────────────────────────────────────────────────────────────────

    OUTPUT_FILE = Path(__file__).parent.parent / f"assets/datawiki_scrape_{date.today():%Y%m%d}.csv" 

    BASE_URL = "https://epi-wiki.erasmusmc.nl"
    WIKI_URL = f"{BASE_URL}/wiki/genrwiki/index.php?title=DataWiki_Generation_R"
    DOWNLOAD_PREFIX = "https://p-epi-wiki.erasmusmc.nl/wiki/data"
    SHAREPOINT_PREFIX = "https://erasmusmc.sharepoint.com"

    DM_REQUEST_VARIANTS = [
        "available on request from datamanagement",
        "available by request from datamanagement",
    ]

    VALID_COHORTS = [
        "Generation R", # "Generation R Next",
    ]

    OTHER_VALID_H2 = [
        "Biomarker", "Microbiome", "Omics",
         # "Syntaxes", "History", "Navigatiemenu", # These should not be scraped
    ]

    SKIP_PATTERNS = [
        # READMEs and Data dictionaries 
        r"^readme",
        r"^datadictionary",
        r"data[ _-]?dictionary", # Any data dictionary mentions (?)
        r"protocol",
        r"variable catalogue",
        r"background info dataset",

        # Specific issues (all lowercase!)
        r"parents oracle study cq", # Link is broken but this should be a pdf... so QC info i guess?
        r"for using 1000genome",
        r"content:", # the contents of a zip file ... 
        r"\.rdata\b",
        r"\.csv\b",


        # Deprecated or preliminary data files 
        r"please do not use this version",  
        r"^\s*preliminary data\s*$",

        # Cross ref patterns - avoid parsing files multiple times (?) 
        r"^see also\b",
        r"^go to\b",
    ]

    CROSS_REF_PATTERNS = []
    return (
        BASE_URL,
        CROSS_REF_PATTERNS,
        DM_REQUEST_VARIANTS,
        DOWNLOAD_PREFIX,
        OTHER_VALID_H2,
        OUTPUT_FILE,
        SHAREPOINT_PREFIX,
        SKIP_PATTERNS,
        VALID_COHORTS,
        WIKI_URL,
    )


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    n_parts = df["file_name"].str.split(" ").str.len()

    # Rows with more than one part (i.e., contains at least one space)
    multi_word = df[n_parts > 1]

    print(f"{len(multi_word)} rows have more than one group")
    multi_word
    return


@app.cell
def _(DataRecord, GenRWikiScraper, OUTPUT_FILE):
    # ── Entry point ──────────────────────────────────────────────────────────────

    if __name__ == "__main__":
        scraper = GenRWikiScraper()
        records = scraper.scrape()

        # Save (tabular) output
        df = DataRecord.to_dataframe(records)
        df.to_csv(OUTPUT_FILE, index=False)

        print(f"\nTotal records: {len(records)}")

        for record in records:
            print(record)
            print("-" * 50)
    return (df,)


@app.cell
def _(ClassVar, Optional, asdict, dataclass, pd):
    # ── Data model ───────────────────────────────────────────────────────────────

    @dataclass
    class DataRecord:
        file_name:   str
        cohort:      str
        period:      str
        data_type:   str
        wiki_path:   str = "" 
        file_url:    Optional[str] = None
        pi:          str = ""
        other_notes: str = ""

        def append_note(self, text: str) -> None:
            # TODO: make more flexible - not only ; 
            sep = "; " if self.other_notes else ""
            self.other_notes += sep + text

        def __str__(self) -> str:
            fields = [
                ("File",          self.file_name),
                ("URL",           self.file_url or ""),
                ("PI",            self.pi),
                ("Notes",         self.other_notes),
                ("Cohort",        self.cohort),
                ("Period",        self.period),
                ("DataType",      self.data_type),
                ("DataWiki path", self.wiki_path),
            ]
            col_width = max(len(label) for label, _ in fields)
            return "\n".join(f"{label:<{col_width}}  {value}" for label, value in fields)

        # Column order for tabular output
        COLUMNS: ClassVar[list[str]] = [
            "file_name", "cohort", "period", "data_type",
            "wiki_path", "file_url", "pi", "other_notes",
        ]

        @staticmethod
        def to_dataframe(records: list["DataRecord"]) -> pd.DataFrame:
            return pd.DataFrame([asdict(r) for r in records], columns=DataRecord.COLUMNS)
    return (DataRecord,)


@app.cell
def _(
    BASE_URL,
    BeautifulSoup,
    CROSS_REF_PATTERNS,
    DM_REQUEST_VARIANTS,
    DOWNLOAD_PREFIX,
    DataRecord,
    OTHER_VALID_H2,
    Optional,
    SHAREPOINT_PREFIX,
    SKIP_PATTERNS,
    VALID_COHORTS,
    WIKI_URL,
    re,
    requests,
):
    # ── Paragraph classifier ─────────────────────────────────────────────────────

    class ParagraphClassifier:
        """Classifies a BeautifulSoup <p> element into a processing category."""

        @staticmethod
        def _text(p) -> str:
            return p.get_text(separator=" ", strip=True)

        @staticmethod
        def _lower(p) -> str:
            return ParagraphClassifier._text(p).lower()

        @staticmethod
        def is_empty(p) -> bool:
            return not ParagraphClassifier._text(p)

        @staticmethod
        def is_skip(p) -> bool:
            lower = ParagraphClassifier._lower(p)
            return any(re.search(pat, lower) for pat in SKIP_PATTERNS)

        @staticmethod
        def is_sharepoint(p) -> bool:
            return bool(p.find("a", href=lambda x: x and x.startswith(SHAREPOINT_PREFIX)))

        @staticmethod
        def is_subheading(p) -> bool:
            """Bold <p> with no download link act as a section label on nested pages."""
            has_bold = bool(p.find("b"))
            has_download = bool(p.find("a", href=lambda x: x and x.startswith(DOWNLOAD_PREFIX)))
            return has_bold and not has_download

        @staticmethod
        def is_cross_ref(p) -> bool:
            lower = ParagraphClassifier._lower(p)
            return any(re.search(pat, lower) for pat in CROSS_REF_PATTERNS)

        @staticmethod
        def is_direct_download(p) -> bool:
            return bool(p.find("a", href=lambda x: x and x.startswith(DOWNLOAD_PREFIX)))

        @staticmethod
        def is_dm_request(p) -> bool:
            lower = ParagraphClassifier._lower(p)
            return any(v in lower for v in DM_REQUEST_VARIANTS)

        @staticmethod
        def is_pi_only(p) -> bool:
            return bool(re.search(r"\bPI:\s*\w", ParagraphClassifier._text(p), re.IGNORECASE))

        @staticmethod
        def is_local_path(p) -> bool:
            return bool(re.search(r"\\\\[\w\-.]", ParagraphClassifier._text(p)))
            # return bool(re.search(r"available in ['\"]?\\\\", ParagraphClassifier._text(p), re.IGNORECASE))


    # ── Paragraph parser ─────────────────────────────────────────────────────────

    class ParagraphParser:
        """Extracts structured fields from a classified <p> element."""

        @staticmethod
        def _text(p) -> str:
            return p.get_text(separator=" ", strip=True)

        @staticmethod
        def _extract_pi(text: str) -> str:
            m = re.search(r"\bPI:\s*([^\n~;]+)", text, re.IGNORECASE)
            return m.group(1).strip().rstrip(".,") if m else ""

        @staticmethod
        def _strip_pi(text: str) -> str:
            return re.sub(r",?\s*\bPI:\s*[^\n~;]+", "", text,
                          flags=re.IGNORECASE).strip().strip(".,: ")

        @staticmethod
        def _split_basket(raw: str) -> tuple[str, str]:
            """Split on 'Add this file to your basket' everything after is either PIs or other notes"""
            try:
                name, notes = raw.split("Add this file to your basket")
            except ValueError:
                name, notes = raw, ""
            return name.strip(), notes.strip()

        @staticmethod
        def _find_dm_trigger(lower_text: str) -> tuple[int, str]:
            for variant in DM_REQUEST_VARIANTS:
                idx = lower_text.find(variant)
                if idx != -1:
                    return idx, variant
            return -1, ""


        def parse_direct_download(self, p) -> tuple[str, str, Optional[str]]:
            """Returns (file_name, pi, other_notes, url)."""
            raw = self._text(p)

            url = p.find("a", href=lambda x: x and x.startswith(DOWNLOAD_PREFIX))["href"]

            # TMP: catch incorrect urls?
            # "https://epi-wiki.erasmusmc.nl/wiki/data"
            # ... only one, ask dm to fix it 

            name, notes = self._split_basket(raw)

            pi = self._extract_pi(notes)
            notes = self._strip_pi(notes)

            return name, pi, notes, url

        def parse_dm_request(self, p) -> tuple[str, str]:
            """Returns (file_name, pi, other_notes)."""
            raw = self._text(p)
            idx, trigger = self._find_dm_trigger(raw.lower())

            # Extract PI from wherever it appears
            pre = raw[:idx]
            post = raw[idx + len(trigger):]

            pi = (self._extract_pi(pre) or self._extract_pi(post))

            name  = self._strip_pi(pre)
            notes = self._strip_pi(post)

            # Fallback: grab filename from <b> or <a> if still empty
            # if not name:
            #     tag  = p.find("b") or p.find("a")
            #     name = tag.get_text(strip=True) if tag else ""
            notes = f'Request from DM {notes}'

            return name, pi, notes

        def parse_pi_only(self, p) -> tuple[str, str]:
            """Returns (file_name, pi). Notes are empty for PI-only paragraphs."""
            raw = self._text(p)
            match = re.search(r"\bPI:\s*", raw, re.IGNORECASE)
            name = raw[:match.start()].strip().rstrip(",. ")
            return name, self._extract_pi(raw)

        def parse_local_path(self, p) -> tuple[str, str]:
            """Returns (file_name, pi, other_notes) for paragraphs containing a UNC network path."""
            raw = self._text(p)

            quotes = "'\"\u2018\u2019\u201c\u201d"

            # Find where the UNC path starts
            # Match an optionally-quoted local path
            path_match = re.search(rf"[{quotes}]?(\\\\[^{quotes}]+?)[{quotes}]?(?=\s|$)", raw)
            if not path_match:
                return raw, "", ""

            path = path_match.group(1).strip()

            pre = raw[:path_match.start()] # everything before the (optional) opening quote
            suffix = raw[path_match.end():].strip() # trailing text, e.g. "(due to filesize)"

            # Remove the lead-in phrase ("available in", "available at", "use file", etc.)
            pre = re.sub(rf",?\s*(available in|available at|use file)\s*[{quotes}]?\s*$",
                     "", pre, flags=re.IGNORECASE).strip()

            # Extract PI from pre if present, then strip it to get the filename
            pi = self._extract_pi(pre) or self._extract_pi(suffix)
            name = self._strip_pi(pre).rstrip(f",. {quotes}(")

            suffix_clean = self._strip_pi(suffix)
        
            # Clean up the note: keep full path including closing ) if present
            other_notes = f"Available at '{path}' {suffix_clean}"
        
            return name, pi, other_notes


    # ── Page scraper ─────────────────────────────────────────────────────────────

    class NestedPageScraper:
        """Scrapes a single nested wiki page and returns a list of DataRecords."""

        def __init__(self, session: requests.Session):
            self.session    = session
            self.classifier = ParagraphClassifier()
            self.parser     = ParagraphParser()


        def scrape(self, page_url: str, context: dict) -> list[DataRecord]:
            response = self.session.get(f"{BASE_URL}/{page_url}", timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            records: list[DataRecord] = []
            last_record: Optional[DataRecord] = None

            # Path segments fixed from the main page: cohort > period > link_label
            base_path = context["wiki_path"] # already built by GenRWikiScraper
            current_label = "" # updated by bold <p> subheadings

            def current_path() -> str:
                return " > ".join(s for s in [base_path, current_label] if s)

            for element in soup.find_all(["p"]):

                p = element
                clf = self.classifier

                if clf.is_empty(p) or clf.is_skip(p) or clf.is_sharepoint(p):
                    continue

                # Bold subheadings are added to the path - they are metadata labels 
                if clf.is_subheading(p):
                    current_label = p.get_text(strip=True)
                    continue

                if clf.is_cross_ref(p):
                    if last_record is not None:
                        last_record.append_note(p.get_text(separator=" ", strip=True))
                    continue

                local_context = {
                    **context,
                    # "data_type": current_label or context["data_type"],
                    "wiki_path": current_path(),
                }
                record = self._parse_paragraph(p, local_context)

                if record is not None:
                    records.append(record)
                    last_record = record
                else:
                    print(f"Problem: ~{p.get_text(separator=' ', strip=True)}~")
                    print(f"  wiki_path: {current_path()}")
                    print("-" * 50)

            return records

        def _parse_paragraph(self, p, context: dict) -> Optional[DataRecord]:
            clf = self.classifier
            par = self.parser

            if clf.is_direct_download(p):
                name, pi, notes, url = par.parse_direct_download(p)
                return DataRecord(**context, 
                                  file_name=name, file_url=url, pi=pi, other_notes=notes)

            if clf.is_dm_request(p):
                name, pi, notes = par.parse_dm_request(p)
                return DataRecord(**context, 
                                  file_name=name, pi=pi, other_notes=notes)
        
            if clf.is_local_path(p):
                name, pi, notes = par.parse_local_path(p)
                return DataRecord(**context, file_name=name, pi=pi, other_notes=notes)
        
            if clf.is_pi_only(p):
                name, pi = par.parse_pi_only(p)
                return DataRecord(**context, file_name=name, pi=pi)


            return None


    # ── Main wiki scraper ─────────────────────────────────────────────────────────

    class GenRWikiScraper:
        """
        Top-level scraper. 
        Parses the Generation R data wiki and returns all discovered DataRecords.
        """

        def __init__(self):
            self.session        = requests.Session()
            self.nested_scraper = NestedPageScraper(self.session)
            self.parser         = ParagraphParser()
            self.records:  list[DataRecord] = []

        def fetch_main_page(self) -> BeautifulSoup:
            response = self.session.get(WIKI_URL, timeout=30)
            assert response.status_code == 200, f"Request failed: {response.status_code}"
            assert "DataWiki" in response.text or "Generation R" in response.text, \
                "Got redirected to login or wrong page — check network/authentication"
            return BeautifulSoup(response.content, "html.parser")

        def scrape(self) -> list[DataRecord]:
            soup  = self.fetch_main_page()
            links = soup.find_all("a", href=lambda x: x and x.startswith(
                ("/wiki/genrwiki/index.php", DOWNLOAD_PREFIX)))

            for link in links:
                self._process_link(link)

            return self.records

        def _build_context(self, link) -> Optional[dict]:
            """
            Extract cohort/period/data_type from headings placed above each link or file name.
            Pre-build wiki_path as: cohort > period > data_type (main page information)
            For nested pages, the NestedPageScraper appends > link_label > bold_subheading.
            """
            h2 = link.find_previous("h2")
            cohort = h2.get_text(strip=True) if h2 else ""

            # ── Special sections: Biomarker / Microbiome / Omics ─────────────────
            if cohort in OTHER_VALID_H2:

                link_text = link.get_text(strip=True)   # e.g. "Generation R Child Biomarker"

                if "Next" in link_text:
                    return None  # not yet handled

                # cohort is "Generation R", data_type comes from the h2 section label
                wiki_path = cohort  # e.g. "Biomarker" — nested scraper will append > link_label

                return {"cohort": "Generation R", "period": "",
                        "data_type": cohort,  # "Biomarker" / "Microbiome" / "Omics"
                        "wiki_path": wiki_path}

            elif cohort not in VALID_COHORTS:
                return None   # Generation R Next etc. not yet handled

            h3 = link.find_previous("h3")
            period = h3.get_text(strip=True) if h3 else ""

            # data_type = nearest preceding bold <p> on the main page
            data_type = ""
            for candidate in link.find_all_previous(["p", "h3"]):
                # Stop if we've hit the h3 boundary
                if candidate.name == "h3":
                    break
                if ParagraphClassifier.is_subheading(candidate):
                    data_type = candidate.get_text(strip=True)
                    break

            wiki_path = " > ".join(s for s in [cohort, period, data_type] if s)

            return {"cohort": cohort, "period": period,
                    "data_type": data_type, "wiki_path": wiki_path}

        def _process_link(self, link) -> None:
            page_url = link["href"]
            context  = self._build_context(link)
            if context is None:
                return

            # ── Direct download on the main page ──────────────────────────────

            if page_url.startswith(DOWNLOAD_PREFIX):
                    parent_text = link.find_parent("p").get_text() if link.find_parent("p") else ""
                    name, notes = ParagraphParser()._split_basket(parent_text)
                    record = DataRecord(
                        **context,
                        file_name = name,
                        file_url = page_url,
                        pi = self.parser._extract_pi(notes),
                        other_notes= self.parser._strip_pi(notes),
                    )
                    self.records.append(record)


            # ── Nested page ───────────────────────────────────────────────────
            # Append the link label to the path before handing off to the nested scraper
            else:
                link_label = link.get_text(strip=True)
                nested_context = {
                    **context,
                    "wiki_path": " > ".join(s for s in [context["wiki_path"], link_label] if s),
                }
                self.records.extend(self.nested_scraper.scrape(page_url, nested_context))

    return (GenRWikiScraper,)


if __name__ == "__main__":
    app.run()
