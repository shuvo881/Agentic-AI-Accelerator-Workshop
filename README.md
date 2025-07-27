# Agentic AI Accelerator Workshop

This repository contains resources, labs, and code for the Agentic AI Accelerator Workshop, including multi-agent systems, custom RAG, and Semantic Kernel examples.

## Project Structure

- `Capstone-Project-MS-/` - [Capstone Project Submodule](Capstone-Project-MS-/README.md)
- `Day-1-Build-Agents-with-Copilot-Studio/` - Day 1 labs and data
- `Day-2-Azure-AI-Agents/` - Day 2 labs and Azure AI agent examples
- `Day-3-Custom-RAG-and-Semantic-Kernel/` - Day 3 custom RAG and Semantic Kernel code
- `Day-4-Developing-AI-App-with-Azure-AI-Foundry/` - Day 4 labs and exercises

## Getting Started

### 1. Clone the Repository

```sh
git clone --recurse-submodules https://github.com/<your-username>/Agentic-AI-Accelerator-Workshop.git
cd Agentic-AI-Accelerator-Workshop
```

If you already cloned without `--recurse-submodules`, initialize submodules with:

```sh
git submodule update --init --recursive
```

### 2. Install Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (if required by any subproject)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (for Azure-related labs)

### 3. Install Python Dependencies

For the Python projects (e.g., in `Semantic-Kernel/Python/`):

```sh
cd Day-3-Custom-RAG-and-Semantic-Kernel/Semantic-Kernel/Python
pip install -r requirements.txt
```

### 4. Running the Multi-Agent System

To run the multi-agent weather app builder:

```sh
cd Day-3-Custom-RAG-and-Semantic-Kernel/Semantic-Kernel/Python
python src/multi_agent.py
```

### 5. Working with the Capstone Project Submodule

The capstone project is included as a submodule in [`Capstone-Project-MS-/`](Capstone-Project-MS-/README.md).

To update the submodule to the latest commit from the remote repository:

```sh
git submodule update --remote Capstone-Project-MS-
```

To work inside the submodule:

```sh
cd Capstone-Project-MS-
# Follow instructions in its own README.md
```

## Additional Notes

- Each lab or subproject may have its own setup and requirements. Refer to the respective `README.md` files for more details.
- For Azure-related labs, ensure you are logged in with `az login` and have the necessary permissions.

---

For more information, see the