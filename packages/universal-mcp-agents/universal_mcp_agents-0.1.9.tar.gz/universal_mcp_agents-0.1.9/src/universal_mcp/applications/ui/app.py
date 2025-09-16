import re
from typing import Literal, TypedDict

import httpx
from loguru import logger
from markitdown import MarkItDown
from universal_mcp.applications.application import BaseApplication


class SeriesItem(TypedDict):
    seriesName: str
    value: float


class ChartDataItem(TypedDict):
    xAxisLabel: str
    series: list[SeriesItem]


class PieChartDataItem(TypedDict):
    label: str
    value: float


class ColumnDefinition(TypedDict):
    key: str
    label: str
    type: Literal["string", "number", "date", "boolean"] | None


class UiApp(BaseApplication):
    """An application for creating UI tools"""

    def __init__(self, **kwargs):
        """Initialize the DefaultToolsApp"""
        super().__init__(name="ui")
        self.markitdown = MarkItDown(enable_plugins=True)

    def create_bar_chart(
        self,
        title: str,
        data: list[ChartDataItem],
        description: str | None = None,
        y_axis_label: str | None = None,
    ):
        """Create a bar chart with multiple data series.

        Args:
            title (str): The title of the chart.
            data (List[ChartDataItem]): Chart data with x-axis labels and series values.
            description (Optional[str]): Optional description for the chart.
            y_axis_label (Optional[str]): Optional label for the Y-axis.

        Tags:
            important
        """
        return "Success"

    def create_line_chart(
        self,
        title: str,
        data: list[ChartDataItem],
        description: str | None = None,
        y_axis_label: str | None = None,
    ):
        """Create a line chart with multiple data series.

        Args:
            title (str): The title of the chart.
            data (List[ChartDataItem]): Chart data with x-axis labels and series values.
            description (Optional[str]): Optional description for the chart.
            y_axis_label (Optional[str]): Optional label for the Y-axis.

        Tags:
            important
        """
        return "Success"

    def create_pie_chart(
        self,
        title: str,
        data: list[PieChartDataItem],
        description: str | None = None,
        unit: str | None = None,
    ):
        """Create a pie chart.

        Args:
            title (str): The title of the chart.
            data (List[PieChartDataItem]): Data for the pie chart with labels and values.
            description (Optional[str]): Optional description for the chart.
            unit (Optional[str]): Optional unit for the values.

        Tags:
            important
        """
        return "Success"

    def create_table(
        self,
        title: str,
        columns: list[ColumnDefinition],
        data: list[dict],
        description: str | None = None,
    ):
        """Create an interactive table with data.

        The table will automatically have sorting, filtering, and search functionality. Note that this only creates a table on the frontend. Do not mix this up with tables from applications like google_sheet, airtable.

        Args:
            title (str): The title of the table.
            columns (List[ColumnDefinition]): Column configuration array.
            data (List[dict]): Array of row objects. Each object should have keys matching the column keys.
            description (Optional[str]): Optional description for the table.

        Tags:
            important
        """
        return "Success"

    def _handle_response(self, response: httpx.Response):
        """
        Handle the HTTP response, returning JSON if possible, otherwise text.
        """
        try:
            return response.json()
        except Exception:
            logger.warning(
                f"Response is not JSON, returning text. Content-Type: {response.headers.get('content-type')}"
            )
            return {
                "text": response.text,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

    def http_get(
        self, url: str, headers: dict | None = None, query_params: dict | None = None
    ):
        """
        Perform a GET request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the GET request to. Example: "https://api.example.com/data"
            headers (dict, optional): Optional HTTP headers to include in the request. Example: {"Authorization": "Bearer token"}
            query_params (dict, optional): Optional dictionary of query parameters to include in the request. Example: {"page": 1}

        Returns:
            dict: The JSON response from the GET request, or text if not JSON.
        Tags:
            get, important
        """
        logger.debug(
            f"GET request to {url} with headers {headers} and query params {query_params}"
        )
        response = httpx.get(url, params=query_params, headers=headers)
        response.raise_for_status()
        return self._handle_response(response)

    def http_post(
        self, url: str, headers: dict | None = None, body: dict | None = None
    ):
        """
        Perform a POST request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the POST request to. Example: "https://api.example.com/data"
            headers (dict, optional): Optional HTTP headers to include in the request. Example: {"Content-Type": "application/json"}
            body (dict, optional): Optional JSON body to include in the request. Example: {"name": "John"}

        Returns:
            dict: The JSON response from the POST request, or text if not JSON.
        Tags:
            post, important
        """
        logger.debug(f"POST request to {url} with headers {headers} and body {body}")
        response = httpx.post(url, json=body, headers=headers)
        response.raise_for_status()
        return self._handle_response(response)

    def http_put(self, url: str, headers: dict | None = None, body: dict | None = None):
        """
        Perform a PUT request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the PUT request to. Example: "https://api.example.com/data/1"
            headers (dict, optional): Optional HTTP headers to include in the request. Example: {"Authorization": "Bearer token"}
            body (dict, optional): Optional JSON body to include in the request. Example: {"name": "Jane"}

        Returns:
            dict: The JSON response from the PUT request, or text if not JSON.
        Tags:
            put, important
        """
        logger.debug(f"PUT request to {url} with headers {headers} and body {body}")
        response = httpx.put(url, json=body, headers=headers)
        response.raise_for_status()
        return self._handle_response(response)

    def http_delete(
        self, url: str, headers: dict | None = None, body: dict | None = None
    ):
        """
        Perform a DELETE request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the DELETE request to. Example: "https://api.example.com/data/1"
            headers (dict, optional): Optional HTTP headers to include in the request. Example: {"Authorization": "Bearer token"}
            body (dict, optional): Optional JSON body to include in the request. Example: {"reason": "obsolete"}

        Returns:
            dict: The JSON response from the DELETE request, or text if not JSON.
        Tags:
            delete, important
        """
        logger.debug(f"DELETE request to {url} with headers {headers} and body {body}")
        response = httpx.delete(url, json=body, headers=headers)
        response.raise_for_status()
        return self._handle_response(response)

    def http_patch(
        self, url: str, headers: dict | None = None, body: dict | None = None
    ):
        """
        Perform a PATCH request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the PATCH request to. Example: "https://api.example.com/data/1"
            headers (dict, optional): Optional HTTP headers to include in the request. Example: {"Authorization": "Bearer token"}
            body (dict, optional): Optional JSON body to include in the request. Example: {"status": "active"}

        Returns:
            dict: The JSON response from the PATCH request, or text if not JSON.
        Tags:
            patch, important
        """
        logger.debug(f"PATCH request to {url} with headers {headers} and body {body}")
        response = httpx.patch(url, json=body, headers=headers)
        response.raise_for_status()
        return self._handle_response(response)

    async def read_file(self, uri: str) -> str:
        """
        This tool aims to extract the main text content from any url.
        When faced with a question you do not know the answer to, call this tool as often as
        needed to get the full context from any file in the user file attachments section.

        Asynchronously converts a URI or local file path to markdown format
        using the markitdown converter.
        Args:
            uri (str): The URI pointing to the resource or a local file path.
                       Supported schemes:
                       - http:// or https:// (Web pages, feeds, APIs)
                       - file:// (Local or accessible network files)
                       - data: (Embedded data)

        Returns:
            A string containing the markdown representation of the content at the specified URI

        Raises:
            ValueError: If the URI is invalid, empty, or uses an unsupported scheme
                        after automatic prefixing.

        Tags:
            convert, markdown, async, uri, transform, document, important
        """
        if not uri:
            raise ValueError("URI cannot be empty")

        known_schemes = ["http://", "https://", "file://", "data:"]
        has_scheme = any(uri.lower().startswith(scheme) for scheme in known_schemes)
        if not has_scheme and not re.match(r"^[a-zA-Z]+:", uri):
            if re.match(r"^[a-zA-Z]:[\\/]", uri):  # Check for Windows drive letter path
                normalized_path = uri.replace("\\", "/")  # Normalize backslashes
                processed_uri = f"file:///{normalized_path}"
            else:  # Assume Unix-like path or simple relative path
                processed_uri = (
                    f"file://{uri}" if uri.startswith("/") else f"file:///{uri}"
                )  # Add leading slash if missing for absolute paths

            uri_to_process = processed_uri
        else:
            # Use the uri as provided
            uri_to_process = uri

        return self.markitdown.convert_uri(uri_to_process).markdown

    def list_tools(self):
        """List all available tool methods in this application.

        Returns:
            list: A list of callable tool methods.
        """
        return [
            self.create_bar_chart,
            self.create_line_chart,
            self.create_pie_chart,
            self.create_table,
            self.http_get,
            self.http_post,
            self.http_put,
            self.http_delete,
            self.http_patch,
            self.read_file,
        ]
