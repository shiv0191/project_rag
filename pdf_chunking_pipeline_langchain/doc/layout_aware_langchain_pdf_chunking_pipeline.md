# Layout-Aware LangChain PDF Chunking Pipeline

## 1. Purpose

This document describes the finalized baseline chunking pipeline built for a complex 119-page clinical guideline PDF:

**2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome**

The pipeline is designed for later integration into a modular Retrieval-Augmented Generation (RAG) system. Its primary goal is not merely to split text by size, but to preserve document reading order, page provenance, layout-sensitive content boundaries, and retrieval-safe metadata.

The finalized baseline uses the LangChain ecosystem for `Document` objects and recursive token-aware splitting, while using PyMuPDF for layout extraction and deterministic geometric reconstruction.

---

## 2. Why a Layout-Aware Pipeline Was Required

The source PDF is not a simple single-column text document. It contains:

- multi-column body text;
- section headings;
- figures and figure captions;
- tables;
- running headers and footers;
- publication furniture;
- page-local layout transitions;
- body text continuing around figures;
- scientific and clinical terminology;
- content that can be damaged by naive extraction order.

A naive page-text extraction strategy can produce incorrect reading order such as:

1. left-column line;
2. right-column line;
3. next left-column line;
4. next right-column line.

It can also merge figure captions into body text, swallow valid body text after a figure marker, retain journal furniture, or create tiny meaningless chunks.

The finalized pipeline therefore treats **layout reconstruction as a preprocessing problem before retrieval chunking**.

---

## 3. Final Architecture

```text
PDF
 ↓
PyMuPDF layout extraction
 ↓
LayoutLine objects with coordinates and font metadata
 ↓
Running-furniture detection
 ↓
Content-type classification
 ↓
Geometric region classification
 ↓
Reading-order reconstruction
 ↓
Body / figure-caption / table separation
 ↓
Body-document cleaning
 ↓
Structural document handling
 ↓
LangChain recursive token-aware splitting
 ↓
Chunk quality gate
 ↓
Final validated retrieval corpus
```

Primary outputs:

```text
output/chunks_final.jsonl
output/rejected_chunks.jsonl
output/figure_captions.jsonl
output/tables.jsonl
output/final_chunk_report.json
```

---

## 4. Pipeline Stages

### 4.1 PDF Layout Extraction

The parser uses **PyMuPDF (`fitz`)** to inspect page text as layout-aware blocks, lines, and spans rather than relying only on flattened page text.

For each extracted line, the pipeline preserves information such as:

- text;
- `x0`, `y0`, `x1`, `y1`;
- page number;
- page width and height;
- font names;
- font sizes;
- boldness;
- source block index;
- source line index.

This information is represented through a `LayoutLine` model and is later used for deterministic layout reconstruction.

### 4.2 Running-Furniture Detection

The parser detects publication furniture using both:

- geometric position near page margins; and
- known textual patterns.

Examples include:

- spaced `J A C C`;
- e-page numbers;
- `Ndumele et al`;
- repeated guideline labels;
- volume/date footer patterns;
- spaced publication footer text.

A key design choice is that text is not removed merely because it resembles a known phrase. Position and pattern evidence are combined to reduce accidental deletion of valid body content.

### 4.3 Content-Type Classification

Each line is classified into a content role such as:

- `body`;
- `heading`;
- `figure_caption`;
- `table`;
- `furniture`.

Classification uses signals including:

- explicit figure patterns;
- explicit table patterns;
- numbered section patterns;
- boldness;
- relative font size;
- known furniture patterns.

### 4.4 Geometric Region Classification

Lines are classified into page regions:

- `left`;
- `right`;
- `full_width`;
- `unknown`.

The classification uses page width, page center, gutter tolerance, line width, and whether a line crosses the center of the page.

This is essential for multi-column scientific PDFs because raw extraction order cannot always be trusted.

### 4.5 Reading-Order Reconstruction

The pipeline reconstructs page order geometrically.

It:

1. identifies full-width structural boundaries;
2. builds vertical bands;
3. orders upper full-width material;
4. orders the left column top-to-bottom;
5. orders the right column top-to-bottom;
6. handles remaining full-width and unknown material deterministically.

This stage addresses the central multi-column problem that motivated the custom layout-aware parser.

### 4.6 Body / Figure / Table Separation

The parser emits separate LangChain `Document` streams for:

- `page_body`;
- `figure_caption`;
- `table`.

The important final correction was to make figure/table capture **geometrically bounded**.

Earlier open-ended logic could activate figure mode at a `FIGURE N` marker and continue swallowing subsequent valid body lines until another heading appeared. This caused a real page-11 continuity failure.

The corrected implementation collects only geometrically adjacent continuation lines using:

- vertical gap;
- same-region evidence;
- horizontal overlap.

This prevents a figure marker from consuming the remainder of a page.

### 4.7 Body Cleaning

Only body documents proceed through the body-cleaning stage.

The cleaner removes known residual publication noise while preserving page metadata and legitimate clinical text.

Figures and tables remain separately available instead of being blindly mixed into the body retrieval corpus.

### 4.8 Structural Handling

Cleaned body documents are converted into structural documents while retaining provenance.

The current finalized run produced:

- 119 cleaned body documents;
- 119 structural documents.

The pipeline preserves metadata needed for later retrieval, debugging, and citation.

### 4.9 Token-Aware Retrieval Splitting

Retrieval-sized chunks are created with LangChain's `RecursiveCharacterTextSplitter`.

Configuration:

```text
Tokenizer measurement: cl100k_base
Maximum chunk size: 500 tokens
Chunk overlap: 75 tokens
```

Boundary preference:

```text
paragraph boundary
 ↓
line boundary
 ↓
sentence-like boundary
 ↓
space
 ↓
character fallback
```

The tokenizer is used for deterministic size measurement. It does not force the future embedding model to use the same tokenizer.

### 4.10 Quality Gate

Candidate chunks are validated before entering the final corpus.

The quality gate checks for:

- empty text;
- missing page metadata;
- missing structural metadata;
- heading-only chunks;
- furniture-only chunks;
- meaningless tiny parser/splitter fragments.

The final tiny-fragment rule is intentionally conservative. It rejects debris such as:

```text
.
,
-
1
()
```

while preserving short meaningful content containing alphabetic information.

A generic rule such as `token_count < 20 => reject` was deliberately avoided because it could remove valid short clinical content.

### 4.11 Final Reindexing and Validation

Accepted chunks are finalized with deterministic identifiers and contiguous indices.

Hard validation checks include:

- missing page metadata;
- missing structural metadata;
- empty chunks;
- chunks over token limit;
- duplicate chunk IDs;
- non-contiguous chunk indices.

---

## 5. Final Verified Results

### Layout Regression Tests

Command:

```powershell
$env:PYTHONPATH = ".\src"
pytest .\tests\test_layout_parser.py -v
```

Verified result:

```text
4 passed
```

Passing tests:

```text
test_page_6_section_order
test_page_11_body_continuity
test_page_11_figure_is_separate
test_all_documents_have_page_metadata
```

These tests specifically protect against previously observed layout failures.

### Final Pipeline Run

Verified final run:

```text
Parsed layout Documents: 157
Document type summary:
  page_body: 119
  table: 18
  figure_caption: 20

Body Documents: 119
Figure Documents: 20
Table Documents: 18
Cleaned Documents: 119
Structural Documents: 119
Candidate chunks: 417
```

Quality gate:

```text
Accepted chunks: 415
Rejected chunks: 2
Rejection counts:
  meaningless_fragment: 2
```

Final validation:

```text
missing_page_metadata: 0
missing_structural_metadata: 0
empty_chunks: 0
over_token_limit: 0
duplicate_chunk_ids: 0
non_contiguous_indices: 0
Page range: 1-119
```

Token statistics:

```text
Minimum tokens: 27
Maximum tokens: 500
Average tokens: 368.83
Median tokens: 421.00
```

Final status:

```text
PASS
```

---

## 6. Important Bugs Found and Corrected

### 6.1 Incorrect Multi-Column Reconstruction

Early approaches classified or reconstructed blocks incorrectly, risking wrong body continuity across left and right columns.

**Correction:** geometric region classification and deterministic column-aware reading order.

### 6.2 Right-Column Misclassification

A center-crossing heuristic incorrectly treated valid right-column lines as spanning content.

**Correction:** region classification based on center position, gutter boundaries, and full-width evidence.

### 6.3 Figure Capture Swallowed Valid Body Text

A stateful figure-capture approach remained active too long. On page 11, valid body content containing `dysfunctional adiposity` disappeared from page body.

**Correction:** bounded geometric figure/table continuation capture.

### 6.4 Residual Publication Furniture

Spaced footer content such as publication date/e-page ranges survived earlier cleaning.

**Correction:** additional margin-aware spaced-footer patterns.

### 6.5 Meaningless One-Token Chunks

The generated corpus contained tiny fragments such as:

```text
.
1
```

**Correction:** conservative `meaningless_fragment` quality-gate validation.

The result improved the accepted-corpus minimum from 1 token to 27 tokens.

---

## 7. Expected Improvements

The following improvements are **expected benefits**, not guaranteed retrieval metrics. They should be measured during retrieval evaluation.

### 7.1 Better Reading-Order Fidelity

**Expected improvement:** fewer chunks containing interleaved left/right column text.

Why:

- ordering is reconstructed geometrically;
- left and right regions are explicitly modeled;
- full-width boundaries are handled separately.

Likely downstream effect:

- more coherent embeddings;
- fewer semantically corrupted chunks;
- better evidence retrieval for questions whose answers span several lines in one column.

### 7.2 Better Body Continuity

**Expected improvement:** reduced loss of valid body paragraphs around figures and tables.

Why:

- atomic figure/table capture is geometrically bounded;
- body text no longer remains trapped in an open-ended figure state.

Likely downstream effect:

- higher recall for facts located near figures;
- fewer missing-answer cases caused by parser segmentation.

### 7.3 Cleaner Retrieval Corpus

**Expected improvement:** lower retrieval pollution from:

- journal headers;
- page footers;
- publication labels;
- isolated punctuation;
- isolated digits;
- other parser debris.

Likely downstream effect:

- fewer irrelevant nearest-neighbor matches;
- reduced embedding budget spent on noise;
- cleaner reranker inputs.

### 7.4 Better Provenance

**Expected improvement:** easier traceability from retrieved chunk back to source page and structural context.

Why:

- page metadata is mandatory;
- structural metadata is mandatory;
- page range validation covers 1–119;
- missing metadata count is zero.

Likely downstream effect:

- easier citations;
- better debugging;
- better retrieval-error analysis.

### 7.5 Better Handling of Non-Body Content

**Expected improvement:** figures and tables can be processed with specialized future strategies instead of being indiscriminately embedded as ordinary prose.

Why:

- 20 figure-caption documents are separated;
- 18 table documents are separated.

Likely downstream effect:

- future table-aware retrieval;
- figure-caption indexing;
- multimodal extensions;
- separate retrieval routing.

### 7.6 More Stable Chunk Sizes

**Expected improvement:** predictable context size for embedding, retrieval, reranking, and generation.

Verified accepted-corpus statistics:

```text
Min: 27 tokens
Max: 500 tokens
Mean: 368.83 tokens
Median: 421 tokens
```

Likely downstream effect:

- fewer pathological micro-chunks;
- no over-limit chunks;
- more consistent retrieval units.

### 7.7 Better Regression Safety

**Expected improvement:** future parser modifications are less likely to silently reintroduce known failures.

Why:

- page-6 order is tested;
- page-11 body continuity is tested;
- page-11 figure separation is tested;
- metadata completeness is tested.

---

## 8. What Is Not Yet Proven

The pipeline should be treated as a **frozen baseline**, not as mathematically perfect.

Current validation proves implemented invariants and targeted regression cases. It does not yet prove:

- optimal Recall@K;
- optimal nDCG@K;
- optimal chunk size;
- optimal overlap;
- perfect reading order on every page;
- perfect table extraction;
- perfect figure interpretation;
- best embedding-model compatibility;
- best performance for every query type.

Therefore, no further speculative parser tuning should be done without evidence.

---

## 9. Baseline Freeze Policy

The following architecture should now remain unchanged unless retrieval evaluation identifies a measurable failure pattern:

```text
layout extraction
→ geometric ordering
→ body/figure/table separation
→ cleaning
→ structural handling
→ token-aware splitting
→ validation
```

Do not change the following merely because another value “might be better”:

- 500-token maximum;
- 75-token overlap;
- layout thresholds;
- region heuristics;
- cleaner rules;
- recursive separators.

A future change should require:

1. a reproducible failure;
2. a representative query or document case;
3. a regression test;
4. before/after retrieval measurement;
5. no regression on existing layout tests.

---

## 10. Recommended Next Phase

The next phase is **retrieval evaluation**, not more chunking redesign.

Recommended sequence:

```text
chunks_final.jsonl
 ↓
embedding/indexing experiment
 ↓
evaluation query set
 ↓
gold relevant pages/chunks
 ↓
retrieval
 ↓
Recall@K / MRR / nDCG@K
 ↓
failure analysis
 ↓
evidence-based pipeline changes only
```

Suggested evaluation categories:

- direct factual questions;
- CKM stage-definition questions;
- recommendation questions;
- risk-assessment questions;
- questions whose answer lies near a figure;
- questions whose answer crosses a paragraph boundary;
- acronym-heavy clinical queries;
- exact terminology queries;
- paraphrased queries.

---

## 11. Modular RAG Integration

The current pipeline is suitable as an ingestion module in a larger modular RAG architecture.

A future modular design can separate:

```text
ingestion
├── layout parser
├── cleaner
├── structural processor
├── retrieval splitter
├── validator
└── corpus writer

indexing
├── embedding provider
├── vector store
└── metadata index

retrieval
├── dense retriever
├── sparse retriever
├── hybrid fusion
└── reranker

generation
├── context builder
├── prompt layer
├── LLM
└── citation formatter

evaluation
├── retrieval metrics
├── generation metrics
└── regression suite
```

This separation allows the chunking baseline to remain stable while retrieval and generation components evolve independently.

---

## 12. Final Assessment

The finalized pipeline is a defensible baseline for this document because it combines:

- layout-aware extraction;
- geometric multi-column ordering;
- separate figure/table handling;
- page provenance;
- LangChain `Document` interoperability;
- token-aware recursive splitting;
- explicit quality gating;
- deterministic validation;
- targeted regression tests.

The strongest reason to stop modifying chunking now is not that the pipeline is guaranteed perfect. It is that the known concrete failures have been corrected, the targeted regression tests pass, the corpus invariants pass, and further changes should now be justified by retrieval evidence rather than speculation.

**Baseline status: FROZEN FOR RETRIEVAL EVALUATION**

