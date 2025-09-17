"""PODataInsight document loader."""

import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, Literal, Optional, Tuple, get_args, overload

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPLIT_CHAR = "\n\n"
DataInsightModeType = Literal["single", "page", "element"]
StrPath = str | Path


class PolarisAIDataInsightLoader(BaseLoader):
    """
    Polaris AI DataInsight Document Loader.

    This loader extracts text, images, and other objects from various document formats.

    Setup:
        Install ``langchain-polaris-ai-datainsight`` and
        set environment variable ``POLARIS_AI_DATA_INSIGHT_API_KEY``.

        ```bash
            pip install -U langchain-polaris-ai-datainsight
            export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
        ```

    Instantiate:
        - Using a file path:

            ```python
            from langchain_community.document_loaders import PolarisAIDataInsightLoader

            loader = PolarisAIDataInsightLoader(
                file_path="path/to/file.docx",
                resources_dir="path/to/save/resources/"
            )
            ```

        - Using file data and filename:

            ```python
            from langchain_community.document_loaders import PolarisAIDataInsightLoader

            loader = PolarisAIDataInsightLoader(
                file=open("path/to/file.docx", "rb").read(),
                filename="file.docx",
                resources_dir="path/to/save/resources/"
            )
            ```

    Lazy load:
        ```python
            docs = []
            docs_lazy = loader.lazy_load()

            for doc in docs_lazy:
                docs.append(doc)

            print(docs[0].page_content[:100])
            print(docs[0].metadata)
        ```
    """

    @overload
    def __init__(
        self,
        *,
        file_path: StrPath,
        api_key: Optional[str],
        resources_dir: Optional[StrPath] = "app/",
        mode: DataInsightModeType = "single",
    ): ...

    @overload
    def __init__(
        self,
        *,
        file: bytes,
        filename: str,
        api_key: Optional[str],
        resources_dir: Optional[StrPath] = "app/",
        mode: DataInsightModeType = "single",
    ): ...

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance.

        The instance can be initialized in two ways:
        1. Using a file path: provide the `file_path` parameter
        2. Using bytes data: provide both `file` and `filename` parameters

        Note:
            If you provide both `file_path` and `file`/`filename`,
            a ValueError will be raised.

        Args:
            `file_path` (str, Path): Path to the file to process.
                Use instead of `file` and `filename`.
            `file` (bytes): Bytes data of the file to process
                . Use instead of `file_path` and must be provided with `filename`.
            `filename` (str): Name of the file when using bytes data.
                Must be provided with `file`.
            `api_key` (str, optional): API authentication key. If not provided,
                the API key will be retrieved from an environment variable.
                If no API key is found, a ValueError is raised.
            `resources_dir` (str, optional): Any images contained in the document as non-text objects will be 
                stored in this directory as separate image files. If the directory does not exist, it will be created.
                Defaults to "app/".
            `mode` (str, optional): Document loader mode. Valid options are "element",
                "page", or "single". Defaults to "single".

        Mode:
            The mode parameter determines how the document is loaded:
                `element`: Load each element in the pages as a separate Document object.
                `page`: Load each page in the document as a separate Document object.
                `single`: Load the entire document as a single Document object.

        Example:
            - Using a file path:

                ```python
                loader = PolarisAIDataInsightLoader(
                    file_path="path/to/file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```

            - Using file data and filename:

                ```python
                loader = PolarisAIDataInsightLoader(
                    file=open("path/to/file.docx", "rb").read(),
                    filename="file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```
        """

        self.mode: DataInsightModeType = kwargs.get("mode")
        self.doc_extractor: PolarisAIDataInsightExtractor = None
        _api_key = kwargs.get(
            "api_key", os.environ.get("POLARIS_AI_DATA_INSIGHT_API_KEY")
        )

        # Check if the file_path is provided
        if "file_path" in kwargs:
            if "file" in kwargs or "filename" in kwargs:
                raise ValueError(
                    "Both file_path and file/filename provided."
                    " Please provide only one valid combination."
                )

            file_path = kwargs["file_path"]

            if not isinstance(file_path, (str, Path)):
                raise ValueError("`file_path` must be a string or Path object.")

            self.doc_extractor = PolarisAIDataInsightExtractor(
                file_path=kwargs["file_path"],
                api_key=_api_key,
                resources_dir=kwargs.get("resources_dir", "app/"),
            )

        # Check if the file is provided
        elif "file" in kwargs and "filename" in kwargs:
            file = kwargs["file"]
            filename = kwargs["filename"]

            if not isinstance(file, bytes):
                raise ValueError("`file` must be a bytes object.")

            if not isinstance(filename, str):
                raise ValueError("`filename` must be a string.")

            self.doc_extractor = PolarisAIDataInsightExtractor(
                file=kwargs["file"],
                filename=kwargs["filename"],
                api_key=_api_key,
                resources_dir=kwargs.get("resources_dir", "app/"),
            )

        else:
            raise ValueError("Either file_path or file/filename must be provided.")

    @property
    def supported_modes(self) -> list[str]:
        return list(get_args(DataInsightModeType))

    def lazy_load(self) -> Iterator[Document]:
        json_data = self.doc_extractor.extract()

        # Convert the JSON data to Document objects
        document_list = self._convert_json_to_documents(json_data)

        yield from document_list

    def _convert_json_to_documents(self, json_data: Dict) -> list[Document]:
        """
        Convert JSON data to Document objects.

        Args:
            json_data (Dict): JSON data to convert.

        Returns:
            list[Document]: List of Document objects.
        """
        if self.mode == "element":
            document_list = []
            for doc_page in json_data["pages"]:
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )
                    document_list.append(
                        Document(
                            page_content=element_content, metadata=element_metadata
                        )
                    )
            return document_list
        elif self.mode == "page":
            document_list = []
            for doc_page in json_data["pages"]:
                page_content = ""
                page_metadata: Dict[str, Any] = {}
                
                # Parse elements in the page
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )
                    # Add element content to page content
                    page_content += element_content + SPLIT_CHAR
                    # Add element metadata to page metadata
                    page_metadata[element_metadata["id"]] = element_metadata

                # Add page document
                document_list.append(
                    Document(page_content=page_content, metadata=page_metadata)
                )
            return document_list
        else:
            doc_content = ""
            doc_metadata: Dict[str, Any] = {}
            # Parse elements in the document
            for doc_page in json_data["pages"]:
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )
                    # Add element content to document content
                    doc_content += element_content + SPLIT_CHAR
                    # Add element metadata to document metadata
                    doc_metadata[element_metadata["id"]] = element_metadata

            return [Document(page_content=doc_content, metadata=doc_metadata)]

    def _parse_doc_element(self, doc_element: Dict) -> Tuple[str, Dict]:
        """Parse a document element and extract its content and metadata.

        Args:
            doc_element (Dict): The document element to parse.

        Returns:
            Tuple[str, Dict]: The extracted content and metadata.
        """
        element_id = doc_element.get("id")
        data_type = doc_element.pop("type")
        content = doc_element.pop("content")

        # Result dictionary
        element_content = ""
        element_metadata = {}

        # Extract the content data based on the data type
        if data_type == "table":
            table_id = f"di.table.{element_id}"
            if "html" not in content:
                raise ValueError(f"Table content not found for {element_id} element")
            
            # Get data from parsing output
            html_table = content.get("html", "")
            html_table = re.sub(r"<table[^>]*>", "<table>", html_table)
            
            element_content = html_table            
            element_metadata = {
                "id": table_id,
                "type": "table"
            }

        elif data_type == "chart":
            # Get data from parsing output
            chart_id = f"di.chart.{element_id}"
            chart_title = content.get("title", "")
            chart_image = content.get("src", "")
            chart_content = content.get("csv", "")
            chart_series_names = content.get("series_names", [])
            chart_x_axis_labels = content.get("x_axis_labels", [])
            chart_y_axis_main_scale = content.get("y_axis_main_scale", [])
            if not chart_image:                
                raise ValueError(f"Image path not found for {chart_image}")
            if not chart_content:
                raise ValueError(f"Chart content not found for {element_id} element")

            # Make content and metadata
            chart_content = chart_content.replace("\r\n", "\n").strip()
            element_content = (
                f'<figure id="{chart_id}" data-category="{data_type}">'
                f'<figcaption> {chart_title} </figcaption>'
                f'<pre data-format="csv"> {chart_content} </pre>'
                f'</figure>'
            )
            element_metadata = {
                "id": chart_id,
                "type": "chart",
                "src": chart_image,
                "series_names": chart_series_names,
                "x_axis_labels": chart_x_axis_labels,
                "y_axis_main_scale": chart_y_axis_main_scale,
            }
        
        elif data_type == "equation":
            # Get data from parsing output
            equation_id = f"di.equation.{element_id}"
            equation_image = content.get("src", "")
            equation_value = content.get("rawMath_value", "")
            equation_format = content.get("rawMath_format", "")
            if not equation_value:
                logger.debug(f"Equation rawMath_value not found for {element_id} element")
            if not equation_format:
                logger.debug(f"Equation rawMath_format not found for {element_id} element")
            
            # Make content and metadata
            element_content = (
                f'<figure id="{equation_id}" data-category="{data_type}">'
                f'<pre data-format="{equation_format}"> {equation_value} </pre>'
                f'</figure>'
            )
            element_metadata = {
                "id": equation_id,
                "type": "equation",
                "src": equation_image,
            }

        elif data_type == "image":
            # Get data from parsing output
            image_id = f"di.image.{element_id}"
            image_path = content.get("src")  # image filename
            if not image_path:
                raise ValueError(f"Image path not found for {image_path}")

            # Make content and metadata
            element_content = f'<img id="{image_id}" data-category="{data_type}"/>'
            element_metadata = {
                "id": image_id,
                "type": "image",
                "src": image_path,
            }
        
        else:   # text, header, footer
            element_id = f"di.text.{element_id}"
            
            element_content = content.get("text", "")
            if not element_content:
                logger.debug(f"Text content not found for {element_id} element")
            
            element_metadata = {
                "id": element_id,
                "type": "text",
            }

        return element_content, element_metadata

    def _validate_data_structure(self, json_data):
        if "pages" not in json_data:
            raise ValueError("Invalid JSON data structure.")
        if "elements" not in json_data["pages"][0]:
            raise ValueError("Invalid JSON data structure.")