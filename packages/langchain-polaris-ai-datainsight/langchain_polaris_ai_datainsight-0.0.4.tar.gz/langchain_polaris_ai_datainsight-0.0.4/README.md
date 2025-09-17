# langchain-polaris-ai-datainsight

This package covers Polaris AI DataInsight integration with LangChain.

Polaris AI DataInsight is a document parser that extracts document elements (text, images, complex tables, charts, etc.) from various file formats into structured JSON, making them easy to integrate into RAG systems.

- Supported document formats : docx, xlsx, pptx, hwpx, hwp
- Supported elements types : text, table, image, chart, shape, header, footer, caption

## Documents

You can refer to the following examples to learn how to work with PolarisAIDataInsightLoader.

1. [How to load documents in langchain](./docs/document_loaders.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PolarisOffice/PolarisAIDataInsight/blob/main/langchain-polaris-ai-datainsight/docs/document_loaders.ipynb)

2. How to build a RAG: [Refer to a `cookbook` directory](./cookbook)

## Installation and Setup

To use PolarisAIDataInsight model, you need to install a python package:

```bash
pip install -U langchain-polaris-ai-datainsight
```

And you should configure credentials by setting the following environment variables:

```bash
export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
```

Refer to [here](https://datainsight.polarisoffice.com/documentation/quickstart) how to get an Polaris AI DataInsight API key.


## Document Loaders


```python
from langchain_polaris_ai_datainsight import PolarisAIDataInsightLoader

loader = PolarisAIDataInsightLoader(
    file_path="path/to/file",
    resources_dir="path/to/dir"
)
```