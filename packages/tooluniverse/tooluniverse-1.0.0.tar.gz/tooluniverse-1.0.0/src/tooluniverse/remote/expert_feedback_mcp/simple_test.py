#!/usr/bin/env python3
"""
Simple Test for Human Expert System
"""

from tooluniverse import ToolUniverse

# Initialize tool universe
tooluni = ToolUniverse()
tooluni.load_tools()

# Test queries for expert feedback tools
test_queries = [
    {"name": "expert_get_expert_status", "arguments": {}},
    {
        "name": "expert_consult_human_expert",
        "arguments": {
            "question": "What is aspirin used for?",
            "specialty": "general",
            "priority": "normal",
            "timeout_minutes": 1,
        },
    },
]

print(tooluni.tool_specification("expert_consult_human_expert"))

for idx, query in enumerate(test_queries):
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    result = tooluni.run(query)
    print("✅ Success. Example output snippet:")
    print(result if isinstance(result, dict) else str(result))
