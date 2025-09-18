# Silu Programming Language
# 斯路编程语言

A simple AI-first interpreted programming language with Python-like syntax, designed as a foundation for advanced AI reasoning capabilities.

## Vision & AI Roadmap

Silu aims to become a platform for developing AI systems that can:
- **Combine rigorous logical reasoning with probabilistic reasoning**
- **Achieve self-bootstrapping and self-correction capabilities** 
- **Conduct autonomous hypothesis testing and experimentation**
- **Discover inconsistencies and drive curiosity-based learning**

### Development Stages
- **2025-2028**: Logic mastery (CFG, data flow, SMT verification)
- **2028-2032**: Logic + probabilistic reasoning fusion  
- **2032-2036**: Self-bootstrapping and self-correction
- **2036-2040**: Hypothesis-driven experimentation
- **2040+**: Inconsistency detection and curiosity-driven knowledge creation

See [AI Development Plan](docs/plan.md) for detailed roadmap and benchmarks.

## Quick Start

### Installation

```bash
# Using pip
pip install -e .

# Using uv (recommended for development)
uv sync && uv pip install -e .
```

### Basic Usage

```bash
# Run a Silu program
silu hello.si

# Check if Python code is compatible with Silu
silu check program.py

# Interactive execution
silu interpret --source "print('Hello, World!')"

# Generate LLVM IR for native compilation
silu ir hello.si --output hello.ir.json
silu llvm hello.ir.json --output hello.ll
```

### Compilation to Native Code

Silu now supports compilation to native machine code via LLVM IR:

```bash
# Complete compilation workflow
silu ir program.si --output program.ir.json  # Generate Silu IR
silu llvm program.ir.json --output program.ll # Convert to LLVM IR
llc program.ll -o program.s                   # Compile to assembly
clang program.s -o program                    # Link to executable
./program                                     # Run native executable
```

### Hello World Example

Create `hello.si`:
```silu
# Variables and basic operations
name = "Silu"
version = 1.0

print("Hello from", name, version)

# Functions
def greet(person):
    return "Welcome to " + person + "!"

message = greet("Silu Programming")
print(message)
```

Run it:
```bash
silu hello.si
```

## Key Features

- **Simple Syntax**: Python-like syntax that's easy to learn
- **Multiple Execution Modes**: 
  - Direct interpretation
  - Python compatibility checking
  - IR (Intermediate Representation) generation and execution
  - Symbolic execution for program analysis
- **Rich Data Types**: int, float, str, bool, bytes, lists, dictionaries
- **Control Flow**: if/elif/else, while loops, for loops with range()
- **Advanced For Loops**: Support for tuple unpacking (`for key, value in dict.items()`)
- **Functions**: User-defined functions with parameters, return values, and closures
- **Built-in Functions**: `print()`, `type()`, `isinstance()`, type conversions, `len()`
- **Dictionary Operations**: Full dictionary support with `.keys()`, `.values()`, `.items()` methods

## Advanced Usage

### Check Python Compatibility
```bash
# Check if a Python file can be interpreted by Silu
silu check program.py
# Output: program.py ok (or program.py bad: specific error reason)

# Examples of error messages:
# program.py bad: syntax error: expected ':' at line 4
# program.py bad: name error: Name 'undefined_var' is not defined  
# program.py bad: runtime error: division by zero
# program.py bad: type error: can only concatenate str (not "int") to str
# program.py bad: empty file
# program.py bad: file not found
```

### Generate Intermediate Representation
```bash
silu ir program.si --format json --output program.ir
```

### Symbolic Execution Analysis
```bash
silu symbolic program.si
```

### Execute IR Directly
```bash
silu exec program.ir
```

### LLVM IR Generation and Native Compilation
```bash
# Generate LLVM IR from Silu IR
silu llvm program.ir.json --output program.ll

# Complete compilation pipeline
silu ir program.si --output program.ir.json    # Generate Silu IR
silu llvm program.ir.json --output program.ll  # Convert to LLVM IR
llc program.ll -o program.s                    # Compile to assembly
clang program.s -o program                     # Link to executable

# Run demo workflow
python demo_silu_to_llvm.py --save-files
```

## Documentation

- **[AI Development Plan](docs/plan.md)** - Long-term AI reasoning roadmap and benchmarks
- **[CLI Usage Guide](docs/cli_usage.md)** - Complete command-line reference
- **[Language Features](docs/language_features.md)** - Syntax and examples  
- **[Development Guide](docs/development.md)** - Setup, testing, and contributing
- **[Symbolic Execution](docs/symbolic_execution.md)** - Program analysis capabilities
- **[IR Design](docs/simple_ir_design.md)** - Intermediate representation format
- **[LLVM IR Generation](docs/llvm_ir_generation.md)** - Native code compilation via LLVM
- **[Interpreter Specification](docs/interpreter_spec.md)** - Core implementation details

## Examples

### Demo Programs

The repository includes comprehensive demo programs showcasing all language features:

```bash
# Run the main demo (variables, functions, control flow)
silu demo.si

# Complex programming patterns
silu complex_example.si

# Symbolic execution analysis
silu symbolic symbolic_demo.si
```

### Performance Comparison

Compare different execution modes:
```bash
# Interpretation vs IR execution
time silu interpret demo.si
silu ir demo.si --output demo.ir.json --format json
time silu exec demo.ir.json
```

## Contributing

We welcome contributions! See the [Development Guide](docs/development.md) for setup instructions and coding guidelines.

## License

MIT License