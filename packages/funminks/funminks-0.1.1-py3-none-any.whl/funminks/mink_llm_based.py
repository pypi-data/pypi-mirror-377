'''
A module for defining an individual in a genetic algorithm (warmly called a mink).
An individual is defined by its genome, which is a list of genes/motifs.
Motifs are primitive and unitary blocks of information that can be combined to form a genome.

The individual (mink) class encapsulates the genome and provides methods for mutation and (eventually) 
crossover.
'''

import random 
import pandas as pd
import math
import types
from typing import Callable, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# CD. Mink
class Mink:
    '''
    A Mink is an individual in the population, represented only by genotype (genome), which is the 
    target of selection.
    
    Attributes:
        genome (str): A representation of code to fit a target function
    Methods:
        
    '''
    def __init__(self, genome:str="", datapoints:str="", prompt:str="", previous_parental_fitness:float=None, llm_params=None):
        '''
        Initialize a Mink instance.
        '''
        self.llm_params = llm_params
        self.previous_parental_fitness = previous_parental_fitness
        self.orig_genome = genome  # genome is a string representing the assembly of motifs
        self.genome = genome
        self.datapoints_path = datapoints  # path to csv file
        try:
            # Parse datapoints string into a pandas DataFrame
            lines = datapoints.strip().split('\n')
            data = [line.split(',') for line in lines if line]
            df = pd.DataFrame(data, columns=['x', 'y']).astype(float)
            self.df_datapoints = df
        except Exception as e:
            raise RuntimeError(f"Failed to read datapoints file '{datapoints}': {e}")
        self.prompt = prompt
        self.fitness_score = None  # fitness score initialized to None

    def is_valid_genome(self, genome: str) -> bool:
        '''
        A check to determine if the genome is valid Python code.
        '''
        try:
            compile(genome, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def mutate(self, mutation_rate=0.1):
        '''
        Calls upon an LLM to generate changes in the code
        '''
        # try 5 times to generate valid code, otherwise keep the original genome
        for _ in range(5):
            new_genome = self.generate_new_code(self.prompt, self.genome, self.datapoints_path)
            if self.is_valid_genome(new_genome):
                self.genome = new_genome
                print(self.genome)
                break

    def calculate_fitness(self, metric: str = 'mse'):
        '''
        Build a function object from the genome string (assumed to be a complete
        Python function definition that includes a `def` line and at least one
        `return` statement) and evaluate it against the datapoints.

        Assumptions / Requirements:
            - self.genome is valid Python code containing at least one function
              definition whose first positional argument is interpreted as the
              independent variable (x).
            - Prefer a function named 'f'; if absent, will use the first
              function object found in the executed namespace.
            - No expression-only genomes are supported (must start with 'def').

        Datapoints CSV is expected to contain at least two columns:
            col0: input variable (x)
            col1: target output (y_true)

        Procedure:
            1. Execute the genome code in a restricted namespace.
            2. Extract callable (prefer 'f').
            3. For each row, compute y_pred = f(x).
            4. Compute regression error between y_pred and y_true.
            5. Fitness = -error (so GA maximizes fitness).

        Parameters
        ----------
        interface parity placeholder).
        metric : One of 'mse', 'mae', 'rmse', 'mape'.

        Returns
        -------
        float fitness value (higher is better). Large negative penalty if failure.
        '''
        df = self.df_datapoints
        if df.shape[1] < 2:
            raise ValueError("Datapoints file must contain at least two columns (x, y)")

        # Extract first two numeric-like columns
        # If headers exist, keep them; otherwise treat generically
        x_col, y_col = df.columns[:2]
        x_vals = df[x_col].values
        y_true = df[y_col].values

        # Build function directly from genome
        code = self.genome.strip()
        if not code or not code.startswith('def'):
            self.fitness_score = -1e12
            return self.fitness_score

        local_ns = {}
        safe_builtins = {
            'abs': abs, 'min': min, 'max': max, 'sum': sum, 'len': len,
            'float': float, 'int': int, 'pow': pow, 'range': range,
        }
        safe_globals = {
            '__builtins__': safe_builtins,
            'math': math,
        }
        try:
            exec(compile(code, '<genome>', 'exec'), safe_globals, local_ns)
        except Exception:
            self.fitness_score = -1e12
            return self.fitness_score

        fn = local_ns.get('f')
        if not isinstance(fn, types.FunctionType):
            # fallback: any function
            for v in local_ns.values():
                if isinstance(v, types.FunctionType):
                    fn = v
                    break
        if not isinstance(fn, types.FunctionType):
            self.fitness_score = -1e12
            return self.fitness_score

        y_pred = []
        for x in x_vals:
            try:
                yp = fn(x)
            except Exception:
                self.fitness_score = -1e12
                return self.fitness_score
            # Guard non-finite results
            if yp is None or (isinstance(yp, float) and (math.isnan(yp) or math.isinf(yp))):
                self.fitness_score = -1e12
                return self.fitness_score
            y_pred.append(yp)

        # Convert to pandas Series for convenience
        y_pred_series = pd.Series(y_pred, index=df.index)

        # Compute error metric
        diff = y_pred_series - y_true
        try:
            if metric == 'mse':
                error = (diff ** 2).mean()
            elif metric == 'rmse':
                error = (diff ** 2).mean() ** 0.5
            elif metric == 'mae':
                error = diff.abs().mean()
            elif metric == 'mape':
                # Avoid division by zero
                denom = pd.Series([d if d != 0 else 1e-12 for d in y_true])
                error = ((diff.abs() / denom).mean()) * 100.0
            else:
                raise ValueError(f"Unsupported metric '{metric}'")
        except Exception:
            # a really bad error if returned as default if something goes wrong
            self.fitness_score = -1e12
            return self.fitness_score

        # Fitness is negative error so GA maximizes fitness
        self.fitness_score = -float(error)
        return self.fitness_score

    def generate_new_code(self, template, code_snippet, datapoints):
        """
        Combines a template (from txt file) and a code snippet to form a prompt.
        Returns the LLM result as a string.
        """
        def trim_result(result):
            """Trims the result to only include the elements within the <FINAL>...</FINAL> tags."""
            start = result.find("<FINAL>")
            end = result.find("</FINAL>")
            if start != -1 and end != -1:
                return result[start + len("<FINAL>"):end].strip()
            return result
        
        # start_token = "<START>"
        # end_token = "<END>"
        # The other methods that retrieve motifs could be used to help stabilize the llm predictions
        # prompt = f"{template}\n\n{start_token}{code_snippet}{end_token}"
        prompt = template.replace("<FUNCTION>", code_snippet).replace("<DATAPOINTS>", datapoints)
        inputs = self.llm_params['tok'](prompt, return_tensors="pt").to(next(self.llm_params['model'].parameters()).device)
        seed = random.randint(0, 2**31 - 1)
        # Seed global RNGs (some backends ignore provided generator for generate in this build/model config)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        
        with torch.inference_mode():
            gen_kwargs = dict(
                do_sample=True,
                temperature=0.7,
                max_new_tokens=512,
                pad_token_id=self.llm_params['tok'].eos_token_id,
            )
            out = self.llm_params['model'].generate(**inputs, **gen_kwargs)
        result = trim_result(self.llm_params['tok'].decode(out[0], skip_special_tokens=True))
        return result
