# Financial Knowledge Graph Extractor

This project transforms unstructured financial news into a structured, navigable **Knowledge Graph**. By leveraging Large Language Models (LLMs) and the `langextract` library, it identifies key entities like companies, executives, and financial events, mapping their relationships into interactive visualizations.



---

## ## Project Overview

The system processes raw text (e.g., market reports or news articles) through a multi-stage pipeline:

1.  **Entity & Relationship Extraction**: Uses a local **Llama 3.1 (8B)** model to identify entities and triples based on a predefined financial schema.
2.  **Data Persistence**: Results are saved in `.jsonl` format for further analysis or integration into other databases.
3.  **Interactive Visualization**: 
    * **Annotated Document**: An HTML view where extracted data is highlighted directly within the source text with a playback feature.
    * **Dynamic Graph**: A `pyvis`-powered network graph allowing users to explore corporate relationships and financial impacts.

---

## ## Core Features

* **Financial Schema**: Specifically tuned to extract Company Names, Tickers, Financial Figures, Dates, Executives, and Sentiment.
* **Relationship Mapping**: Automatically links entities through predicates such as `ISSUES`, `PARTNERS_WITH`, `AFFECTED_BY`, and `OUTPERFORMS`.
* **Local Execution**: Designed to run with **Ollama**, ensuring data privacy by processing text locally.
* **Visual Debugging**: The generated HTML includes a step-by-step playback of extractions, making it easy to verify model accuracy.

---

## ## Tech Stack

* **Language**: Python
* **LLM Interface**: `langextract` (utilizing Ollama for Llama 3.1)
* **Graph Engine**: `networkx`
* **Visualization**: `pyvis` (Network Graph) and `langextract` (Annotated HTML)

---

## ## File Descriptions

| File | Purpose |
| :--- | :--- |
| **`main.py`** | The primary script containing the extraction logic, relationship mapping, and visualization calls. |
| **`financial_information_extractions.jsonl`** | The structured output containing raw extraction data and character offsets. |
| **`financial_information_extractions.html`** | A high-readability, interactive annotation of the source document. |
| **`financial_information_graph.html`** | A standalone HTML file containing the interactive Knowledge Graph. |

---

## ## Getting Started

### ### 1. Prerequisites
Ensure you have **Ollama** installed and the Llama 3.1 model downloaded:
```bash
ollama pull llama3.1:8b
```
### ### 2. Installation
Install the necessary Python dependencies
```bash
pip install -r requirements.txt
```

### ### 3. Execution
Run the pipeline
```bash
pyhton main.py
```

## ## Example  Relationships Extracted

Based on the provided automotive industry sample text:

* **General Motors** $\rightarrow$ `ISSUES` $\rightarrow$ **GM**
* **Ford** $\rightarrow$ `AFFECTED_BY` $\rightarrow$ **Novelis** (due to fire incident)
* **Rivian** $\rightarrow$ `INVESTED_IN_BY_FORD` $\rightarrow$ **Ford**
* **GM** $\rightarrow$ `OUTPERFORMS` $\rightarrow$ **Ford**