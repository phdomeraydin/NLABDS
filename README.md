# Lie Signature OOP Experiment

Object-oriented reorganization of the supplied class-2 nilpotent Lie algebra digital-signature benchmark.

## Structure

- `src/config.py` - experiment parameters
- `src/algebra.py` - finite-field helpers and Lie algebra class
- `src/crypto.py` - KeyGen, Sign, Verify
- `src/attacks.py` - Gaussian elimination and linearization attack
- `src/benchmark.py` - benchmark runner and statistics
- `src/reporting.py` - CSV tables and PNG figures
- `src/app.py` - end-to-end application
- `main.py` - entry point
- `results/` - generated output

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Output

Tables 2-10 are written as CSV files. Figures are written as 300-dpi PNG files. The Key Generation, Signing, and Verification means are plotted together as a grouped column chart with exact values above the bars.

The numerical benchmark values remain run-dependent because execution time depends on the machine and runtime environment. The mathematical experiment logic and fixed random seeds follow the supplied code.
