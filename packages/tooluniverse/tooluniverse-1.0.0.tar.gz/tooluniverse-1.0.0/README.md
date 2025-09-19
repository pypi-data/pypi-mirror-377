# ToolUniverse

[![ToolUniverse-PIP](https://img.shields.io/badge/Pip-ToolUniverse-blue)](https://pypi.org/project/tooluniverse/)
[![ToolUniverse](https://img.shields.io/badge/Code-ToolUniverse-purple)](https://github.com/mims-harvard/ToolUniverse)
[![Model context protocol (MCP)](https://img.shields.io/badge/Model_Context_Protocol_(MCP)_Supported-green)](README_USAGE.md#running-the-mcp-server)
[![Documentation](https://img.shields.io/badge/Documentation-Available-green)](https://zitniklab.hms.harvard.edu/bioagent/)
[![Web Service](https://img.shields.io/badge/Web_Service-aiscientist.tools-blue)](https://aiscientist.tools)

**Democratizing AI Scientists for Collaborative Discovery** 🌐 [Web Service](https://aiscientist.tools) | 📦 [PyPI](https://pypi.org/project/tooluniverse) | 📚 [Documentation](https://zitniklab.hms.harvard.edu/bioagent/)


ToolUniverse is an ecosystem for creating AI scientist systems from any open or closed large language model (LLM). It standardizes how LLMs identify and call tools, integrating more than **600 machine learning models, datasets, APIs, and scientific packages** for data analysis, knowledge retrieval, and experimental design.

## What is ToolUniverse?

AI scientists are emerging computational systems that serve as collaborative partners in discovery. However, these systems remain difficult to build because they are bespoke, tied to rigid workflows, and lack shared environments that unify tools, data, and analysts into a common ecosystem.

ToolUniverse addresses this challenge by providing a standardized ecosystem that transforms any AI model into a powerful research scientist. By abstracting capabilities behind a unified interface, ToolUniverse wraps around any AI model (LLM, AI agent, or large reasoning model) and enables users to create and refine entirely custom AI research assistants without additional training or finetuning.

**Key Features:**

- **AI-Tool Interaction Protocol**: Standardized interface governing how AI scientists issue tool requests and receive results
- **Universal AI Model Support**: Works with any LLM, AI agent, or large reasoning model (GPT, Claude, Gemini, open models)
- **Find Tool & Call Tool Operations**: Maps natural-language descriptions to tool specifications and executes tools with structured results
- **Tool Composition & Workflows**: Chains tools for sequential or parallel execution in self-directed workflows
- **Continuous Expansion**: New tools can be registered locally or remotely without additional configuration

<!-- ![TxAgent](img/TxAgent_ToolUniverse.jpg) -->

## 🚀 Quick Start

**Build your first AI scientist in 5 minutes:**

```python
# 1. Install ToolUniverse
pip install tooluniverse

# 2. Create AI scientist system
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()  # Load 600+ scientific tools

# 3. Use Find Tool operation to discover relevant tools
tools = tu.run({
    "name": "Tool_Finder_Keyword",
    "arguments": {"query": "disease target associations"}
})

# 4. Use Call Tool operation to execute selected tool
result = tu.run({
    "name": "OpenTargets_get_associated_targets_by_disease_efoId",
    "arguments": {"efoId": "EFO_0000249"}  # Alzheimer's disease
})
```

**Success!** Your AI scientist can now reason, experiment, and collaborate in discovery using the AI-tool interaction protocol.

→ **Complete Quick Start Tutorial**: [Quick Start Tutorial](https://zitniklab.hms.harvard.edu/bioagent/quickstart.html)


## 📦 Installation

### Recommended Installation (uv)

```bash
uv add tooluniverse
```

### Standard Installation (pip)

```bash
pip install tooluniverse
```


### Development Installation

```bash
git clone https://github.com/mims-harvard/ToolUniverse.git
cd ToolUniverse
uv sync  # or pip install -e .[dev]
```

→ **Complete Installation Tutorial**: [Installation Tutorial](https://zitniklab.hms.harvard.edu/bioagent/installation.html)

## 🔧 Usage & Integration

ToolUniverse supports multiple integration methods for different use cases:

### Python SDK Integration

```python
from tooluniverse import ToolUniverse

# Initialize and load tools
tu = ToolUniverse()
tu.load_tools()

# Find relevant tools
tools = tu.run({
    "name": "Tool_Finder_Keyword",
    "arguments": {"query": "protein structure prediction"}
})

# Execute tools
result = tu.run({
    "name": "UniProt_get_protein_info",
    "arguments": {"gene_symbol": "BRCA1"}
})
```

### AI Assistant Integration

**🖥️ Claude Desktop**: Native integration with Claude AI assistant → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/claude_desktop.html)
**💻 Claude Code**: Claude Code environment integration → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/claude_code.html)
**🔮 Gemini CLI**: Google's AI agent integration → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/gemini_cli.html)
**🧠 Qwen Code**: AI scientist integration with Qwen Code environment → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/qwen_code.html)
**⚡ GPT Codex CLI**: Terminal-based AI scientist with Codex CLI → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/codex_cli.html)
**🎯 ChatGPT API**: OpenAI integration via MCP protocol and function calling → [Setup Tutorial](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/chatgpt_api.html)

→ **AI Assistant Setup Guides**: [Building AI Scientists](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/index.html)

### MCP Server Integration

```bash
# Start MCP server
python -m tooluniverse.smcp_server

# Or with CLI
tooluniverse-mcp --help
```

### Core Capabilities

- **🔍 Find Tool Operation**: Maps natural-language descriptions to tool specifications using semantic search
- **⚙️ Call Tool Operation**: Executes selected tools with structured arguments and returns text, embeddings, or JSON
- **🔗 Tool Composition**: Chains tools for sequential or parallel execution in self-directed workflows
- **🛠️ Tool Creation**: Automatically creates new tools from natural language descriptions
- **🔄 Iterative Optimization**: Refines tool interfaces and specifications for correct use by AI scientists
- **🌐 Shared Environment**: Unifies tools, data, and analysts into a common ecosystem for interoperability and reuse

→ **Detailed Usage Tutorial**: [README_USAGE.md](README_USAGE.md)
→ **Complete Getting Started**: [Getting Started Tutorial](https://zitniklab.hms.harvard.edu/bioagent/getting_started.html)


## 📚 Documentation

Our comprehensive documentation covers everything from quick start to advanced workflows:

### 🚀 Getting Started
- **[Quick Start Tutorial](https://zitniklab.hms.harvard.edu/bioagent/quickstart.html)**: 5-minute setup and first query
- **[Installation](https://zitniklab.hms.harvard.edu/bioagent/installation.html)**: Complete installation options
- **[Getting Started](https://zitniklab.hms.harvard.edu/bioagent/getting_started.html)**: Step-by-step tutorial
- **[AI-Tool Protocol](https://zitniklab.hms.harvard.edu/bioagent/guide/interaction_protocol.html)**: Understanding the interaction protocol

### 📖 User Guides
- **[Loading Tools](https://zitniklab.hms.harvard.edu/bioagent/guide/loading_tools.html)**: Complete Tutorial to loading tools
- **[Tool Discovery](https://zitniklab.hms.harvard.edu/bioagent/tutorials/finding_tools.html)**: Find tools by keyword, LLM, and embedding search
- **[Tool Caller](https://zitniklab.hms.harvard.edu/bioagent/guide/tool_caller.html)**: Primary execution engine
- **[Tool Composition](https://zitniklab.hms.harvard.edu/bioagent/guide/tool_composition.html)**: Chain tools into workflows
- **[Scientific Workflows](https://zitniklab.hms.harvard.edu/bioagent/guide/scientific_workflows.html)**: Real-world research scenarios

### 🤖 Building AI Scientists
- **[Overview](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/index.html)**: Create AI research assistants from any LLM
- **[Claude Desktop Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/claude_desktop.html)**: Native MCP integration with Claude Desktop App
- **[Claude Code Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/claude_code.html)**: AI scientist development in Claude Code environment
- **[Gemini CLI Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/gemini_cli.html)**: Command-line scientific research with Google Gemini
- **[Qwen Code Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/qwen_code.html)**: AI scientist workflows in Qwen Code environment
- **[GPT Codex CLI Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/codex_cli.html)**: Terminal-based research with OpenAI Codex
- **[ChatGPT API Integration](https://zitniklab.hms.harvard.edu/bioagent/guide/building_ai_scientists/chatgpt_api.html)**: Programmatic research with ChatGPT function calling

### 🛠️ Advanced Features
- **[Hooks System](https://zitniklab.hms.harvard.edu/bioagent/guide/hooks/index.html)**: Intelligent output processing
- **[Expert Feedback](https://zitniklab.hms.harvard.edu/bioagent/tutorials/expert_feedback.html)**: Human-in-the-loop consultation
- **[Agentic Tools](https://zitniklab.hms.harvard.edu/bioagent/tutorials/agentic_tools_tutorial.html)**: AI-powered tool development
- **[Case Study](https://zitniklab.hms.harvard.edu/bioagent/tutorials/tooluniverse_case_study.html)**: End-to-end drug discovery workflow

### 🔧 Expanding ToolUniverse
- **[Architecture](https://zitniklab.hms.harvard.edu/bioagent/expand_tooluniverse/architecture.html)**: System architecture overview
- **[Local Tool Registration](https://zitniklab.hms.harvard.edu/bioagent/expand_tooluniverse/local_tool_registration.html)**: Create custom tools
- **[Remote Tool Registration](https://zitniklab.hms.harvard.edu/bioagent/expand_tooluniverse/remote_tool_registration.html)**: Integrate external services
- **[Contributing Tools](https://zitniklab.hms.harvard.edu/bioagent/expand_tooluniverse/comprehensive_tool_guide.html)**: Complete contribution Tutorial

### 📚 API Reference
- **[API Directory](https://zitniklab.hms.harvard.edu/bioagent/api_directory.html)**: Complete tool listing
- **[Tools Reference](https://zitniklab.hms.harvard.edu/bioagent/api/tools_complete_reference.html)**: Detailed API documentation
- **[Quick Reference](https://zitniklab.hms.harvard.edu/bioagent/api_quick_reference.html)**: Essential API Tutorial

### 🆘 Help & Support
- **[FAQ](https://zitniklab.hms.harvard.edu/bioagent/faq.html)**: Frequently asked questions
- **[Troubleshooting](https://zitniklab.hms.harvard.edu/bioagent/troubleshooting.html)**: Common issues and solutions
- **[Help Index](https://zitniklab.hms.harvard.edu/bioagent/help/index.html)**: Support resources

→ **Browse All Documentation**: [ToolUniverse Documentation](https://zitniklab.hms.harvard.edu/bioagent/)

## 🚀 AI Scientists Projects Powered by ToolUniverse

### TxAgent: AI Agent for Therapeutic Reasoning

**TxAgent** is an AI agent for therapeutic reasoning that leverages ToolUniverse's comprehensive scientific tool ecosystem to solve complex therapeutic reasoning tasks.

[![ProjectPage](https://img.shields.io/badge/Page-TxAgent-red)](https://zitniklab.hms.harvard.edu/TxAgent) [![PaperLink](https://img.shields.io/badge/Arxiv-TxAgent-red)](https://arxiv.org/pdf/2503.10970) [![TxAgent-PIP](https://img.shields.io/badge/Pip-TxAgent-blue)](https://pypi.org/project/txagent/) [![TxAgent](https://img.shields.io/badge/Code-TxAgent-purple)](https://github.com/mims-harvard/TxAgent) [![HuggingFace](https://img.shields.io/badge/HuggingFace-TxAgentT1-yellow)](https://huggingface.co/collections/mims-harvard/txagent-67c8e54a9d03a429bb0c622c)

---

*Building your own project with ToolUniverse? We'd love to feature it here! Submit your project via [GitHub Issues](https://github.com/mims-harvard/ToolUniverse/issues) or contact us.*

## 🌍 Ecosystem & Community

### Democratizing AI Agents for Science

ToolUniverse addresses the fundamental challenge that AI scientists remain difficult to build because they are bespoke, tied to rigid workflows, and lack shared environments. Drawing inspiration from how unified ecosystems have transformed omics research by enabling interoperability, reuse, and community-driven development, ToolUniverse provides comparable infrastructure for AI scientists.

**Core Principles:**

- **🔓 Unified Ecosystem**: Integrates tools, data, and analysts into a common environment like omics platforms
- **📐 Standardized Protocol**: AI-tool interaction protocol analogous to HTTP for internet communication
- **🔗 Interoperability**: Tool specification schema that standardizes definitions and enables consistent inference
- **🌐 Collaborative Discovery**: Enables AI scientists to serve as computational partners in research
- **🚀 Scalable Construction**: Builds AI scientists at scale without bespoke implementation

### Research Applications

**🧬 Drug Discovery & Development**
- Target identification and validation
- Compound screening and optimization
- Safety and toxicity assessment
- Clinical trial analysis and outcomes
- **Case Study**: Hypercholesterolemia research where ToolUniverse enabled an AI scientist to identify a potent drug analog with favorable predicted properties

**🔬 Molecular Biology Research**
- Gene function annotation and analysis
- Protein structure prediction and modeling
- Pathway analysis and network construction
- Disease association studies

**📊 Literature & Knowledge Mining**
- Automated systematic literature reviews
- Named entity recognition and extraction
- Citation network analysis and mapping
- Patent landscape analysis and IP research

**🤖 AI-Driven Research Automation**
- Hypothesis generation and testing
- Experimental design optimization
- Multi-modal data analysis and integration
- Results interpretation and reporting

### Community & Support

**Get Involved:**
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/mims-harvard/ToolUniverse/issues)
- 💬 **Join Discussions**: [GitHub Discussions](https://github.com/mims-harvard/ToolUniverse/discussions)
- 📧 **Contact**: Visit [aiscientist.tools](https://aiscientist.tools) for more information
- 🤝 **Contribute**: See our [Contributing Tutorial](https://zitniklab.hms.harvard.edu/bioagent/expand_tooluniverse/comprehensive_tool_guide.html)

**Integrations & Extensions:**
- **Model Context Protocol (MCP)**: Full MCP server support for AI assistant integration
- **Claude Desktop**: Native integration with Anthropic's Claude Desktop App
- **OpenAI Function Calling**: Direct integration with ChatGPT and GPT models
- **Custom Agents**: Build domain-specific AI research assistants

## Citation

```
@misc{gao2025txagent,
      title={TxAgent: An AI Agent for Therapeutic Reasoning Across a Universe of Tools},
      author={Shanghua Gao and Richard Zhu and Zhenglun Kong and Ayush Noori and Xiaorui Su and Curtis Ginder and Theodoros Tsiligkaridis and Marinka Zitnik},
      year={2025},
      eprint={2503.10970},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2503.10970},
}
```

##  Contact & Contributors

### Contact

For questions, suggestions, or collaboration opportunities:

- **📧 Contact**: [Shanghua Gao](mailto:shanghuagao@gmail.com)
- **🌐 Web Platform**: [aiscientist.tools](https://aiscientist.tools)
- **💻 GitHub**: [github.com/mims-harvard/ToolUniverse](https://github.com/mims-harvard/ToolUniverse)

### Contributors

- **[Shanghua Gao](https://shgao.site)**
- **[Richard Zhu](https://www.linkedin.com/in/richard-zhu-4236901a7/)**
- **[Pengwei Sui](mailto:pengwei_sui@hms.harvard.edu)**
- **[Zhenglun Kong](https://zlkong.github.io/homepage/)**
- **[Sufian Aldogom](mailto:saldogom@mit.edu)**
- **[Yepeng Huang](mailto:yepeng_huang@hms.harvard.edu)**
- **[Ayush Noori](https://www.ayushnoori.com/)**
- **[Reza Shamji](mailto:reza_shamji@hms.harvard.edu)**
- **[Krishna Parvataneni](mailto:krishna_parvataneni@hms.harvard.edu)**
- **[Theodoros Tsiligkaridis](https://sites.google.com/view/theo-t)**
- **[Marinka Zitnik](https://zitniklab.hms.harvard.edu/)**



### Acknowledgments

ToolUniverse is developed by the [Zitnik Lab](https://zitniklab.hms.harvard.edu/) at Harvard Medical School in collaboration with MIT Lincoln Laboratory. We thank the scientific community for their valuable feedback and contributions.

---

**🧬🤖🔬 Happy researching with ToolUniverse!**

*Democratizing AI agents for science - one tool at a time.*
