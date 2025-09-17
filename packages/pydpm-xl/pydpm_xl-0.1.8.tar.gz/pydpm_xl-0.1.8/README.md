# pyDPM

A Python library for DPM-XL (Data Point Model eXtensible Language) data processing, migration, and semantic analysis. pyDPM provides functionality to migrate Access databases to SQLite, validate DPM-XL expressions syntactically and semantically, and perform comprehensive data dictionary validation.

## Features

- **Database Migration**: Convert Access databases (.mdb/.accdb) to SQLite with automatic fallback support
- **Expression Validation**: Three-tier validation system (syntax → semantics → data dictionary)
- **DPM-XL Support**: Full language support with ANTLR4-based parsing
- **Cross-platform**: Works on Linux, Windows, and macOS
- **API & CLI**: Both programmatic API and command-line interface

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

### Database Migration Requirements

The migration system supports multiple methods for reading Access databases:

1. **mdbtools** (Linux/Unix, recommended): Install system package for better performance
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mdbtools

   # macOS
   brew install mdbtools
   ```

2. **access_parser** (Pure Python fallback): Automatically used if mdbtools unavailable
   - Cross-platform Python library
   - No external dependencies required
   - Included with pyDPM installation

## Usage

### Database Migration

Migrate Access database to SQLite:

```bash
poetry run pydpm migrate-access ./path-to-release.accdb
```

This creates a SQLite database with migrated tables and views for DPM data access.

### Expression Validation

#### Syntax Validation

Validate DPM-XL expression syntax:

```bash
poetry run pydpm syntax "sum({Table1, row A})"
```

#### Semantic Validation

Perform comprehensive semantic analysis:

```bash
poetry run pydpm semantic "{Table1, row A} + {Table1, row B}"
```

Semantic validation includes:
- Type checking and inference
- Symbol resolution
- Dependency analysis
- Data dictionary consistency

### DPM-XL Expression Examples

```dpm-xl
# Basic cell reference
{Table1, row A, col 1}

# Arithmetic operations
{Sales, Q1} + {Sales, Q2}

# Aggregations with grouping
sum({Revenue} group by {Country})

# Conditional expressions
if {Status} = "Active" then {Amount} else 0

# Time operations
{Sales} timeshift Q, 1

# Filtering
{Revenue}[{Country} = "US"]

# With clauses for simplification
with {FinancialData}: {Revenue} - {Costs}
```

