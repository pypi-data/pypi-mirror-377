import requests
import re
from typing import Dict, Any, List
from .base_tool import BaseTool
from .tool_registry import register_tool

ALPHAFOLD_BASE_URL = "https://alphafold.ebi.ac.uk/api"


@register_tool("AlphaFoldRESTTool")
class AlphaFoldRESTTool(BaseTool):
    """
    AlphaFold Protein Structure Database API tool.
    Supports queries by UniProt accession ID.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        fields = tool_config.get("fields", {})
        parameter = tool_config.get("parameter", {})

        self.endpoint_template: str = fields["endpoint"]
        self.param_schema: Dict[str, Any] = parameter.get("properties", {})
        self.required: List[str] = parameter.get("required", [])
        self.output_format: str = fields.get("return_format", "JSON")

    def _build_url(self, arguments: Dict[str, Any]) -> Dict[str, Any] | str:
        url_path = self.endpoint_template
        placeholders = re.findall(r"\{([^{}]+)\}", url_path)
        for ph in placeholders:
            if ph not in arguments or arguments[ph] is None:
                return {"error": f"Missing required parameter '{ph}'"}
            url_path = url_path.replace(f"{{{ph}}}", str(arguments[ph]))
        return ALPHAFOLD_BASE_URL + url_path

    def run(self, arguments: Dict[str, Any]):
        # Validate required params
        missing = [k for k in self.required if k not in arguments]
        if missing:
            return {"error": f"Missing required parameter(s): {', '.join(missing)}"}

        url = self._build_url(arguments)
        if isinstance(url, dict) and "error" in url:
            return url
        try:
            resp = requests.get(
                url,
                timeout=30,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/AlphaFold",
                },
            )
        except Exception as e:
            return {"error": "Request to AlphaFold API failed", "detail": str(e)}

        # Handle HTTP errors cleanly
        if resp.status_code == 404:
            return {
                "error": "No AlphaFold prediction found",
                "uniprot_id": arguments.get("uniprot_id"),
            }
        if resp.status_code != 200:
            return {
                "error": f"AlphaFold API returned {resp.status_code}",
                "detail": resp.text,
            }

        # Parse JSON
        if self.output_format.upper() == "JSON":
            try:
                data = resp.json()
                if not data:
                    return {
                        "error": "AlphaFold returned an empty response",
                        "uniprot_id": arguments.get("uniprot_id"),
                    }

                return {
                    "data": data,
                    "metadata": {
                        "count": len(data) if isinstance(data, list) else 1,
                        "source": "AlphaFold Protein Structure DB",
                        "endpoint": url,
                        "query": arguments,
                    },
                }
            except Exception as e:
                return {
                    "error": "Failed to parse JSON response",
                    "raw": resp.text,
                    "detail": str(e),
                }

        # Fallback if non-JSON format
        return {"data": resp.text, "metadata": {"endpoint": url}}
