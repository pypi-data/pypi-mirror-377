# polaris-ai-datainsight

This package is Python SDK for Polaris AI DataInsight.

Polaris AI DataInsight is a document parser that extracts document elements (text, images, complex tables, charts, etc.) from various file formats into structured JSON, making them easy to integrate into RAG systems.

- Supported document formats :  docx, xlsx, pptx, hwpx, hwp
- Supported elements types : text, table, image, chart, shape, header, footer, caption

## Installation and Setup

You need to install a python package:

```bash
pip install -U polaris-ai-datainsight
```

And you should configure credentials by setting the following environment variables:

```bash
export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
```

Refer to [here](https://datainsight.polarisoffice.com/documentation/quickstart) how to get an Polaris AI DataInsight API key.


## Document Extractor

Set the file path to extract and the directory path to store resource files included in the file:

```python
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

loader = PolarisAIDataInsightExtractor(
    file_path="path/to/file",
    resources_dir="path/to/dir"
)
```

Extract document data:

```python
dict_data = loader.extract()
```