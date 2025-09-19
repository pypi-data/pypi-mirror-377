import json
from typing import Any, Dict, List
import os
from tooluniverse import ToolUniverse

# Load expected schema fields dynamically from the JSON definition
schema_path = os.path.join(
    os.path.dirname(__file__), "..", "data", "alphafold_tools.json"
)
with open(schema_path) as f:
    schema = json.load(f)[0]["return_schema"]["properties"]

tooluni = ToolUniverse()
tooluni.load_tools()

# Test cases: 3 valid, 1 invalid UniProt ID, and 1 missing parameter
test_queries: List[Dict[str, Any]] = [
    {
        "name": "alphafold_get_prediction_by_uniprot_id",
        "arguments": {"uniprot_id": "Q14596"},
    },
    {
        "name": "alphafold_get_prediction_by_uniprot_id",
        "arguments": {"uniprot_id": "Q9BUR4"},
    },
    {
        "name": "alphafold_get_prediction_by_uniprot_id",
        "arguments": {"uniprot_id": "Q8W3K0"},
    },
    {
        "name": "alphafold_get_prediction_by_uniprot_id",
        "arguments": {"uniprot_id": "XXX123"},
    },  # invalid
    {
        "name": "alphafold_get_prediction_by_uniprot_id",
        "arguments": {},
    },  # missing param
]

for idx, query in enumerate(test_queries, 1):
    uid = query["arguments"].get("uniprot_id")
    label = f"UniProt ID: {uid}" if uid else "No UniProt ID"
    print(f"\n[{idx}] Running {query['name']} with {label}")
    result = tooluni.run(query)

    # Handle errors
    if isinstance(result, dict) and "error" in result:
        print(f"INVALID: {result['error']}")
        if "detail" in result:
            print(f"   Detail: {result['detail']}")
        continue

    # Handle success
    data = result.get("data", [])
    if not data:
        print("No data returned.")
        continue

    first = data[0]
    print("SUCCESS")
    print(f"   {first.get('uniprotDescription')} ({first.get('uniprotAccession')})")
    print(f"   Organism: {first.get('organismScientificName')}")
    print(f"   Avg pLDDT: {first.get('globalMetricValue')}")
    print(f"   Structure (PDB): {first.get('pdbUrl')}")

    # Schema validation
    missing = [k for k in schema.keys() if k not in first]
    if missing:
        print(f"   INVALID Missing expected fields: {missing}")
    else:
        print("   All expected schema fields present")
