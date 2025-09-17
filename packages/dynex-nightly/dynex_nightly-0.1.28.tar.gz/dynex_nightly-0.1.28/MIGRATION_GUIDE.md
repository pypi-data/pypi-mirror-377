# Migration Guide from Dynex SDK v0.1.x to v2.x (Nightly)

## Overview of Changes

The new version of Dynex SDK (v2.x nightly) represents a significant update with improved architecture, new API, and expanded capabilities. Key changes include:

- **New configuration system** with environment variable priority
- **Improved architecture** with modular separation
- **New model types** (CQM, DQM)
- **Updated API** with better error handling
- **Enhanced logging system**

## 1. Installation

### Old Version (v0.1.x)
```bash
pip install dynex
```

### New Version (v2.x nightly)
```bash
pip install dynex-nightly
```

## 2. Major Import Changes

### Old Version
```python
import dynex
# All functions available directly through dynex
```

### New Version
```python
import dynex
from dynex import DynexConfig, DynexAPI
# Now need to explicitly import configuration and API classes
```

## 3. Configuration System

### Old Version
```python
# Configuration through dynex.ini file
# Parameters passed directly to functions
model = dynex.BQM(bqm, logging=True)
sampler = dynex.DynexSampler(model, mainnet=False)
```

### New Version
```python
# New configuration system with ENV priority
config = DynexConfig(
    solver_version=2,
    mainnet=False,
    is_logging=True
)

model = dynex.BQM(bqm, config=config)
sampler = dynex.DynexSampler(model, config=config)
```

### Environment Variables (NEW)
```bash
export DYNEX_API_KEY=your-key
export DYNEX_API_SECRET=your-secret
export DYNEX_API_ENDPOINT=https://api.dynex.dev
export DYNEX_FTP_HOSTNAME=ftp.dynex.dev
export DYNEX_FTP_USERNAME=your-username
export DYNEX_FTP_PASSWORD=your-password
```

## 4. Model Creation

### BQM (Binary Quadratic Model)

#### Old Version
```python
import dynex
import dimod

bqm = dimod.BinaryQuadraticModel({'x1': 1.0, 'x2': -1.5}, 
                                 {('x1', 'x2'): 1.0}, 
                                 0.0, dimod.BINARY)
model = dynex.BQM(bqm, logging=True)
```

#### New Version
```python
import dynex
import dimod
from dynex import DynexConfig

config = DynexConfig(solver_version=2, mainnet=False)
bqm = dimod.BinaryQuadraticModel({'x1': 1.0, 'x2': -1.5}, 
                                 {('x1', 'x2'): 1.0}, 
                                 0.0, dimod.BINARY)
model = dynex.BQM(bqm, config=config)
```

### SAT (Boolean Satisfiability)

#### Old Version
```python
clauses = [[1, -2, 3], [-1, 4, 5], [6, 7, -8]]
model = dynex.SAT(clauses, logging=True)
```

#### New Version
```python
clauses = [[1, -2, 3], [-1, 4, 5], [6, 7, -8]]
config = DynexConfig(solver_version=1, mainnet=True)
model = dynex.SAT(clauses, config=config)
```

### CQM (Constrained Quadratic Model) - NEW

```python
import dimod
from dynex import DynexConfig

config = DynexConfig(solver_version=2, mainnet=False)

# Creating CQM model
num_widget_a = dimod.Integer('num_widget_a', upper_bound=7)
num_widget_b = dimod.Integer('num_widget_b', upper_bound=3)
cqm = dimod.ConstrainedQuadraticModel()
cqm.set_objective(-3 * num_widget_a - 4 * num_widget_b)
cqm.add_constraint(num_widget_a + num_widget_b <= 5, label='total widgets')

model = dynex.CQM(cqm, config=config)
```

### DQM (Discrete Quadratic Model) - NEW

```python
import dimod
from dynex import DynexConfig

config = DynexConfig(solver_version=2, mainnet=False)

# Creating DQM model
cases = ["rock", "paper", "scissors"]
dqm = dimod.DiscreteQuadraticModel()
dqm.add_variable(3, label='my_hand')
dqm.add_variable(3, label='their_hand')

model = dynex.DQM(dqm, config=config)
```

## 5. Sampler

### Old Version
```python
sampler = dynex.DynexSampler(
    model, 
    logging=True, 
    mainnet=False, 
    description='My Job'
)
sampleset = sampler.sample(
    num_reads=32, 
    annealing_time=100,
    debugging=False
)
```

### New Version
```python
config = DynexConfig(solver_version=2, mainnet=False, is_logging=True)
sampler = dynex.DynexSampler(
    model, 
    config=config,
    description='My Job'
)
sampleset = sampler.sample(
    num_reads=32, 
    annealing_time=100,
    debugging=False,
    is_cluster=True,
    cluster_type=1,
    shots=1,
    rank=1
)
```

## 6. New Sampler Parameters

### New parameters in sample() method:

- `is_cluster=True` - use cluster mode
- `cluster_type=1` - cluster type
- `shots=1` - number of shots
- `rank=1` - solution rank
- `preprocess=False` - preprocessing

### Enhanced parameters:

- `solver_version=2` - new solver version (default)
- `minimum_stepsize=0.05` - minimum step size
- `switchfraction=0.0` - fraction of variables to replace

## 7. Result Processing

### Old Version
```python
sampleset = sampler.sample(num_reads=32, annealing_time=100)
print(sampleset.first.sample)
print(sampleset.first.energy)
```

### New Version
```python
sampleset = sampler.sample(num_reads=32, annealing_time=100)
print(sampleset.first.sample)
print(sampleset.first.energy)

# Additional solution information
print(f"Number of solutions: {len(sampleset)}")
print(f"Best energy: {sampleset.first.energy}")
```

## 8. Quantum Circuits (DynexCircuit)

### Old Version
```python
# Support was limited
```

### New Version
```python
from dynex import DynexCircuit

# Creating quantum circuit
circuit = DynexCircuit()
# ... circuit setup ...
model = circuit.to_model()
sampler = dynex.DynexSampler(model, config=config)
```

## 9. API and Utilities

### Old Version
```python
# Limited API
dynex.test()
dynex.sample_qubo(Q, offset)
```

### New Version
```python
from dynex import DynexAPI, DynexConfig

# Extended API
api = DynexAPI(config=config)
status = api.account_status()
print(f"Account status: {status}")

# Utilities
dynex.test()
dynex.sample_qubo(Q, offset)
```

## 10. Complete Migration Example

### Old Code
```python
import dynex
import dimod
from pyqubo import Array

# Creating BQM
N = 15
K = 5
numbers = [4.8, 4.3, 2.9, 3.2, 0.6, 1.3, 2.3, 1.2, 2.2, 3.6, 4.6, 2.6, 3.4, 0.3, 4.3]
q = Array.create('q', N, 'BINARY')
H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K) ** 2
model = H.compile()
Q, offset = model.to_qubo(index_label=True)
bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)

# Creating model and sampler
model = dynex.BQM(bqm, logging=True)
sampler = dynex.DynexSampler(model, mainnet=False, description='Test Job')

# Sampling
sampleset = sampler.sample(num_reads=32, annealing_time=100)
print(sampleset.first.sample)
```

### New Code
```python
import dynex
import dimod
from pyqubo import Array
from dynex import DynexConfig

# Configuration
config = DynexConfig(
    solver_version=2,
    mainnet=False,
    is_logging=True
)

# Creating BQM
N = 15
K = 5
numbers = [4.8, 4.3, 2.9, 3.2, 0.6, 1.3, 2.3, 1.2, 2.2, 3.6, 4.6, 2.6, 3.4, 0.3, 4.3]
q = Array.create('q', N, 'BINARY')
H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K) ** 2
model = H.compile()
Q, offset = model.to_qubo(index_label=True)
bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)

# Creating model and sampler
model = dynex.BQM(bqm, config=config)
sampler = dynex.DynexSampler(model, config=config, description='Test Job')

# Sampling with new parameters
sampleset = sampler.sample(
    num_reads=32, 
    annealing_time=100,
    is_cluster=True,
    cluster_type=1,
    shots=1,
    rank=1
)
print(sampleset.first.sample)
print(f"Best energy: {sampleset.first.energy}")
```

## 11. Configuration File

### Old dynex.ini
```ini
[DYNEX]
api_key = your_key
api_secret = your_secret
api_endpoint = https://api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = ftp.dynex.dev
ftp_username = your_username
ftp_password = your_password
```

### New dynex.ini (compatible)
```ini
[DYNEX]
api_key = your_key
api_secret = your_secret
api_endpoint = https://api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = ftp.dynex.dev
ftp_username = your_username
ftp_password = your_password
```

## 12. Backward Compatibility

The new version maintains backward compatibility for core functions, but it's recommended to:

1. **Update imports** - add `from dynex import DynexConfig`
2. **Use new configuration system** - create `DynexConfig` object
3. **Update sampler calls** - pass `config` instead of individual parameters
4. **Use new parameters** - `is_cluster`, `shots`, `rank` for better performance

## 13. Benefits of New Version

1. **Better performance** - new solver v2
2. **Extended capabilities** - CQM and DQM support
3. **Improved configuration** - environment variable priority
4. **Better error handling** - more informative messages
5. **Modular architecture** - easier to maintain and extend
6. **Cluster support** - improved scalability

## 14. Frequently Asked Questions

### Q: Can I use old code without changes?
A: Partially. Core functions work, but it's recommended to update to get all benefits.

### Q: How to set up environment variables?
A: Create a `.env` file or export variables in shell:
```bash
export DYNEX_API_KEY=your_key
export DYNEX_API_SECRET=your_secret
```

### Q: Which solver version is better?
A: Version 2 (default) provides better performance and accuracy.

### Q: How to use new CQM/DQM model types?
A: Create a model using `dimod.ConstrainedQuadraticModel` or `dimod.DiscreteQuadraticModel`, then use `dynex.CQM()` or `dynex.DQM()`.

## 15. Support

For help:
- Documentation: [link to documentation]
- Examples: `dynex_sandbox/examples/` folder
- Issues: [link to repository]

---

**Note**: This version is a nightly build and may contain unstable features. For production, it's recommended to use the stable version.
