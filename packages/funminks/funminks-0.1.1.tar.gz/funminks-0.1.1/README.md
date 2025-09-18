<p align="center">
    <img src="./icons/main_logo.png" alt="FunMinks Logo"/>
</p>

# FunMinks: Genetic Algorithm Utilities for LLMs

FunMinks is a Python package for symbolic regression and genetic algorithm experimentation using Large Language Models (LLMs). It provides tools to define, mutate, and evolve code-based individuals ("minks") and manage populations, leveraging LLMs for code generation and mutation.

## What is FunMinks?

FunMinks enables evolutionary computation on code snippets, using LLMs to mutate and optimize Python functions to fit target data. It is designed for symbolic regression, automated code improvement, and research in genetic programming with LLMs.

- **Mink**: An individual represented by a genome (Python code), evaluated for fitness against datapoints.
- **Population**: A collection of minks, managed for selection, mutation, and evolution.
- **LLM Endpoint**: Utilities to load and interact with local LLM models for code generation.

## Features
- Symbolic regression using genetic algorithms and LLMs
- Population management and selection
- Code mutation via LLM prompts
- Fitness evaluation against custom datapoints
- Extensible for custom genetic operations

## Installation

It is recommended to use a virtual environment for isolation:

```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install FunMinks and dependencies
pip install -e .
```

Or install from source:

```powershell
pip install git+https://github.com/UGarCil/GeneticAlgoLLM.git
```

### Requirements
- Python >= 3.10
- [transformers](https://pypi.org/project/transformers/)
- [pandas](https://pypi.org/project/pandas/)
- [huggingface_hub](https://pypi.org/project/huggingface-hub/)
- torch (optional, see below)

If you need GPU support, install the appropriate version of torch:
```powershell
pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
```

## Usage

### 1. Prepare Data and Templates
- Place your datapoints in `templates/datapoints.csv` (two columns: x, y)
- Use or modify `templates/prompt_template.txt` for LLM mutation prompts
- Use `templates/seed_code_template.txt` as the initial genome

### 2. Load LLM Endpoint
```python
from FunMinks.llm_endpoint import load_llm
llm_params = load_llm('path/to/your/model')
```

### 3. Create a Population
```python
from FunMinks.population import Population
from FunMinks.mink_llm_based import Mink

# Load templates and datapoints
with open('templates/prompt_template.txt') as f:
    prompt = f.read()
with open('templates/seed_code_template.txt') as f:
    seed_code = f.read()
with open('templates/datapoints.csv') as f:
    datapoints = f.read()

# Initialize population
pop = Population(
    pop_size=20,
    seed_code=seed_code,
    datapoints=datapoints,
    prompt=prompt,
    llm_params=llm_params
)
```

### 4. Run Evolution
```python
for generation in range(10):
    pop.run_episode()
    print(f"Generation {generation}: Avg fitness = {pop.avg_fitness}")
```

## Project Structure
```
FunMinks/
    mink_llm_based.py   # Mink class (individual)
    population.py       # Population management
    llm_endpoint.py     # LLM loading utilities
icons/
    main_logo.png       # Project logo
templates/
    datapoints.csv      # Example data
    prompt_template.txt # LLM prompt template
    seed_code_template.txt # Initial code genome
```

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Author
Uriel Garcilazo Cruz

## Links
- [Homepage](https://ugarcil.github.io/GeneticAlgoLLM/)
- [Repository](https://github.com/UGarCil/GeneticAlgoLLM)
- [Bug Tracker](https://github.com/UGarCil/GeneticAlgoLLM/issues)

