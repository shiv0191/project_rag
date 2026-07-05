# Local PDF Chunking Pipeline

## Implementation and Design Documentation

**Source document:** 119-page 2026 CKM clinical guideline PDF\
**Environment:** Windows PowerShell · Python 3.11.5 · Local execution

------------------------------------------------------------------------

## 1. Purpose

This document records the completed V1 chunking pipeline for a complex
scientific/medical PDF containing multi-column prose, figures, captions,
tables, running publication furniture, references, appendices, and
changing page layouts.

The output is a traceable JSONL corpus. Embeddings and vector-database
ingestion are intentionally outside scope.

------------------------------------------------------------------------

## 2. Final Pipeline

``` text
Input PDF
    ↓
PyMuPDF4LLM full-document parsing
(page_chunks=True)
    ↓
Persist page-aware intermediate artifact
output/parsed_pages.json
    ↓
Automatic parse validation
    ↓
Cleaning and V1 primary-corpus boundary
    ↓
Heading-aware, structure-first chunk generation
    ↓
Reject known malformed content classes
    ↓
Automatic chunk acceptance gate
    ↓
Bounded finalization
    ↓
output/chunks_final.jsonl
```

------------------------------------------------------------------------

## 3. Key Architectural Decision

The initial low-level PyMuPDF approach successfully reconstructed a
known two-column region, but required page-specific geometry such as
fixed vertical thresholds and custom column rules.

Other pages used different layouts, including:

-   full-width figures,
-   full-width captions,
-   two-column prose,
-   complex scientific tables,
-   changing content regions.

Continuing that approach would have created a fragile custom
document-layout parser rather than a reliable chunking pipeline.

**Decision:** stop extending page-specific geometry heuristics and use
PyMuPDF4LLM as the primary layout-aware parser.

The earlier geometry scripts remain useful diagnostics but are not part
of the final pipeline.

------------------------------------------------------------------------

## 4. Environment and Dependencies

Verified environment:

-   Windows PowerShell
-   Python 3.11.5
-   Virtual environment: `venv`
-   PyMuPDF 1.28.0
-   PyMuPDF4LLM 1.28.0

### `requirements.txt`

``` text
PyMuPDF==1.28.0
pymupdf4llm==1.28.0
```

------------------------------------------------------------------------

## 5. Pipeline Artifacts

  Artifact                                Role
  --------------------------------------- ------------------------------------------
  `src/parse_pdf.py`                      Parse complete PDF page-by-page
  `src/validate_parsed.py`                Automatic parse quality checks
  `src/generate_chunks.py`                V2 cleaning and structure-aware chunking
  `src/accept_chunks.py`                  Machine acceptance gate
  `src/finalize_chunks.py`                Create final V1 corpus
  `output/parsed_pages.json`              Persisted page-aware parser output
  `output/validation_report.json`         Parse validation report
  `output/chunks_v2.jsonl`                Pre-finalization V2 corpus
  `output/rejected_blocks.jsonl`          Excluded-content traceability
  `output/chunk_acceptance_report.json`   Acceptance report
  `output/chunks_final.jsonl`             Final corpus
  `output/final_chunk_summary.json`       Final corpus statistics

------------------------------------------------------------------------

## 6. Stage A --- Full PDF Parsing

The complete PDF is parsed once with PyMuPDF4LLM.

`page_chunks=True` is intentional because later chunks require page
provenance.

Core call:

``` python
pages = pymupdf4llm.to_markdown(
    str(PDF_PATH),
    page_chunks=True,
    show_progress=True,
)
```

Each persisted page record stores:

-   `pdf_page_index`
-   `pdf_page_number`
-   `text`
-   `text_length`
-   `metadata`

Extraction output is persisted before chunking so parsing and chunking
remain independently reproducible and debuggable.

### Observed parse result

  Metric                               Result
  -------------- ----------------------------
  Parsed pages                        119/119
  Empty pages                               0
  Artifact         `output/parsed_pages.json`

------------------------------------------------------------------------

## 7. Stage B --- Automatic Parse Validation

The validator performs bounded corpus-level checks rather than
open-ended manual page inspection.

It:

-   computes median page character count,
-   detects empty pages,
-   flags pages below 500 characters,
-   flags pages above `1.75 × median`,
-   finds repeated lines appearing on at least five pages.

### Observed validation result

  Metric                   Result
  ------------------------ ------------------------------------
  Total pages              119
  Median page characters   5,323
  Empty pages              None
  Short page               Page 8: 334 characters
  Repeated furniture       JACC volume/date line on 118 pages

Pages 84--108 showed unusually high text volume. Later auditing found
reference-style and appendix content with column-interleaving problems,
so this was handled as a content-class issue rather than a simple size
anomaly.

------------------------------------------------------------------------

## 8. Stage C --- Chunking Strategy

The chunker is **structure-first**, not page-first and not
fixed-window-first.

It creates a document-level stream while preserving page provenance.

### Processing rules

1.  Clean known recurring publication furniture.
2.  Limit the V1 primary clinical corpus to pages 1--83.
3.  Split parsed Markdown into logical blocks on blank-line boundaries.
4.  Recognize Markdown headings.
5.  Maintain heading hierarchy.
6.  Treat headings as pending context.
7.  Do not emit heading-only chunks.
8.  Reject conservatively detected malformed table blocks.
9.  Accumulate semantic content toward the target size.
10. Split oversized blocks by sentence boundaries.
11. Use word-window splitting only as the final oversized-block
    fallback.
12. Merge tiny chunks only when neighboring section context matches.
13. Preserve provenance and stable IDs.

### Sizing policy

  Parameter                   Value
  ------------------------- -------
  Target words                  320
  Maximum words                 450
  Minimum preferred words        60
  Normal overlap               None

Word count is intentionally an approximation at this stage.

Exact token-budget enforcement should later use the tokenizer of the
selected embedding model. This avoids coupling the chunking pipeline
prematurely to a specific model.

------------------------------------------------------------------------

## 9. Primary-Corpus Boundary

The V1 semantic corpus is intentionally bounded to pages **1--83**.

Audit evidence showed that page 84 onward contained reference-style
content and later appendix material where multi-column extraction could
become interleaved.

Rather than embedding known-corrupted text, those pages are kept outside
the primary V1 corpus.

Excluded content is preserved in:

``` text
output/rejected_blocks.jsonl
```

This is a V1 corpus policy, not a claim that pages 84--119 are
permanently unusable. A later pipeline may parse references, appendices,
and complex tables with specialized strategies.

------------------------------------------------------------------------

## 10. Malformed Table Policy

Complex scientific tables can be badly interleaved during text
extraction.

The V2 chunker uses conservative corruption signals and rejects strongly
malformed tables instead of embedding scrambled text as ordinary prose.

This avoids contaminating future similarity search with semantically
corrupted text.

------------------------------------------------------------------------

## 11. Stage D --- Automatic Acceptance Gate

The acceptance script applies predetermined hard-failure rules.

This was introduced specifically to prevent an endless manual
inspect-and-tweak cycle.

### Hard checks

-   No empty chunk text.
-   No chunk above 450 words.
-   No heading-only chunks.
-   No known running publication furniture.
-   All page provenance within pages 1--83.
-   No strong reference-number interleaving signal.
-   Chunk indices must be contiguous.
-   Chunk IDs must be unique.

### Acceptance result before finalization

  Check                               Observed result
  --------------------------------- -----------------
  Total chunks                                    213
  Contiguous indices                             True
  Unique chunk IDs                               True
  Empty failures                                    0
  Oversized failures                                0
  Heading-only failures                             0
  Running furniture failures                        9
  Invalid-page failures                             0
  Reference-interleaving failures                   0
  Very short `<20` word warnings                    1
  Short `<60` word warnings                        10

------------------------------------------------------------------------

## 12. Stage E --- Finalization

Under the fixed V1 decision rule, nine chunks flagged for
running-furniture contamination were removed mechanically.

The original V2 corpus remains preserved for traceability.

Final chunks were:

-   reindexed,
-   assigned contiguous indices,
-   given regenerated stable IDs.

### Final corpus result

  Metric                                          Final value
  ----------------------------- -----------------------------
  Input V2 chunks                                         213
  Removed contaminated chunks                               9
  Final chunks                                            204
  Minimum words                                             8
  Maximum words                                           437
  Average words                                        208.84
  Page range                                            1--83
  Final artifact                  `output/chunks_final.jsonl`

------------------------------------------------------------------------

## 13. Final Chunk Schema

Example:

``` json
{
  "chunk_id": "ckm-guideline:00042:<hash>",
  "chunk_index": 42,
  "text": "...",
  "word_count": 231,
  "page_numbers": [20, 21],
  "page_start": 20,
  "page_end": 21,
  "section_path": [
    "Section",
    "Subsection"
  ],
  "source": "ckm_guideline_2026"
}
```

### Metadata purpose

-   `chunk_id`: stable chunk identifier
-   `chunk_index`: ordered corpus position
-   `text`: retrieval content
-   `word_count`: approximate size
-   `page_numbers`: all contributing PDF pages
-   `page_start`: first source page
-   `page_end`: last source page
-   `section_path`: semantic heading context
-   `source`: source-document identifier

------------------------------------------------------------------------

## 14. Reproduction Commands

Run the pipeline in this order:

``` powershell
python .\src\parse_pdf.py
```

``` powershell
python .\src\validate_parsed.py
```

``` powershell
python .\src\generate_chunks.py
```

``` powershell
python .\src\accept_chunks.py
```

``` powershell
python .\src\finalize_chunks.py
```

The authoritative downstream artifact is:

``` text
output/chunks_final.jsonl
```

------------------------------------------------------------------------

## 15. Important Limitations

### 15.1 Pages 84--119 are excluded

The final V1 corpus is **not a full-document semantic index**.

It covers pages:

``` text
1–83
```

### 15.2 Nine contaminated chunks were removed as whole chunks

If a flagged chunk contained both running furniture and useful clinical
prose, useful content may also have been excluded from V1.

### 15.3 One final chunk contains only 8 words

It remains because shortness was treated as a warning rather than a hard
failure.

### 15.4 Complex malformed tables are rejected

They are not repaired in V1.

### 15.5 Chunk sizing uses words

It does not yet use the tokenizer of a future embedding model.

### 15.6 Embeddings are outside scope

No embedding model is selected or executed in this pipeline.

### 15.7 Vector database ingestion is outside scope

No vector database is configured in this pipeline.

------------------------------------------------------------------------

## 16. Recommended Future Improvements

These are optional later improvements and are not required to consider
the current chunking stage complete.

1.  Enforce exact token limits with the selected embedding model
    tokenizer.
2.  Recover pages 84--119 with a dedicated reference/appendix parsing
    path.
3.  Parse complex tables with a table-specialized strategy.
4.  Replace whole-chunk furniture removal with span-level cleaning when
    maximum recall is required.
5.  Add retrieval evaluation after embeddings are introduced.

------------------------------------------------------------------------

## 17. Completion Status

The chunking pipeline is complete as a **bounded V1 implementation**.

The authoritative output for future downstream work is:

``` text
output/chunks_final.jsonl
```

Intermediate artifacts and rejection manifests should be retained for:

-   reproducibility,
-   debugging,
-   traceability,
-   future parser improvements.
