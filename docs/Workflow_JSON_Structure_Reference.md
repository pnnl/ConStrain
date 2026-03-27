# ConStrain Workflow JSON Structure Guide

## Overview

A **Workflow** is a directed graph of execution states that orchestrate ConStrain verification tasks. Workflows are defined in JSON format and executed sequentially, with control flow managed through states, choices, and payload passing.

---

## Top-Level Structure

Every workflow JSON must contain these root properties:

### `workflow_name` (string, required)
A descriptive name for the workflow.

**Example:**
```json
"workflow_name": "G36 Demo workflow"
```

### `meta` (object, required)
Metadata about the workflow. Must contain exactly these four fields:

| Field | Type | Description |
|-------|------|-------------|
| `author` | string | Name of the workflow author |
| `date` | string | Last modified date in `MM/DD/YYYY` format |
| `version` | string | Version number (e.g., "1.0", "2.1") |
| `description` | string | Narrative description of what the workflow does |

**Example:**
```json
"meta": {
  "author": "ConStrain Team",
  "date": "06/29/2023",
  "version": "1.0",
  "description": "Demo workflow to showcase G36 verification item development"
}
```

### `imports` (array, required)
Python import statements required by the workflow. Each string is a valid Python import line (e.g., `"numpy as np"`).

**Example:**
```json
"imports": [
  "numpy as np",
  "pandas as pd",
  "datetime",
  "glob"
]
```

Imported modules can be used in MethodCall expressions and Choice conditions.

**Important: ConStrain API Classes Are Pre-Imported**
All classes from `constrain.api` are automatically available in MethodCall and Choice expressions. Do **not** include them in the imports array. Pre-imported classes include:
- `DataProcessing` (data processing methods)
- `VerificationCase` (verification case management)
- `Verification` (verification setup and execution)
- `Reporting` (result reporting)

**Import Processing Rules:**
- Imports starting with `"import constrain."` or `"from constrain."` are skipped (ConStrain API already imported)
- Statements starting with `"from "` are executed as-is (e.g., `"from numpy import array"`)
- Module-only imports have leading `"import "` stripped if present to avoid duplication
- All imports are executed in the global scope, making them available in MethodCall and Choice expressions

### `working_dir` (string, optional)
An optional working directory path for the workflow execution. If specified:
- The workflow engine changes to this directory before running states
- Directory is created if it doesn't exist
- Cross-platform path handling (Linux and Windows paths are auto-converted)
- Original working directory is restored after workflow completion

**Example:**
```json
"working_dir": "./demo/G36_demo"
```

### `states` (object, required)
A dictionary mapping state names (keys) to state definitions (values). The workflow execution follows the graph defined by states and their transitions.

**Constraints:**
- Must have at least one state
- State names are arbitrary strings (e.g., "load data", "validate cases")
- Exactly one state should have `"Start": "True"` (entry point)
- At least one state should have `"End": "True"` (exit point)
- No circular dependencies are allowed

---

## State Types

Every state must have a `Type` property that determines its behavior:

### Type 1: MethodCall

A **MethodCall** state executes a Python function or method and optionally stores results in the Payloads dictionary.

#### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `Type` | string | Must be `"MethodCall"` |
| `MethodCall` | string | Python expression that resolves to a callable |
| `Parameters` | object \| array | Arguments to pass to the callable |

#### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| `Payloads` | object | How to capture and store the result |
| `Next` | string | Name of the next state (if absent, workflow continues to next unmatched state) |
| `Start` | string | `"True"` to mark as entry point (only one state should have this) |
| `End` | string | `"True"` to mark as exit point (stops workflow execution) |

#### MethodCall Expression

The `MethodCall` string is evaluated as Python code to resolve the actual callable. Examples:

- `"DataProcessing"` → the class itself (calls `__init__`)
- `"DataProcessing.add_parameter"` → class method (shorthand for `constrain.api.data_processing.DataProcessing.add_parameter`)
- `"VerificationCase.load_verification_cases_from_json"` → class method
- `"Payloads['verification_obj'].run"` → method on a stored object
- `"Payloads['obj'].some_method"` → nested method call
- `"glob.glob"` → module-level function (requires import)
- `"print"` → built-in function

**ConStrain API Methods Shorthand Notation:**
All methods from `constrain.api` are pre-imported and available using their class name directly. For example:
- Full qualified name: `constrain.api.data_processing.DataProcessing.add_parameter`
- Shorthand in MethodCall: `"DataProcessing.add_parameter"`

You **do not** need to import `DataProcessing` — it's automatically available.

**Critical Implementation Detail:**
The MethodCall expression is evaluated in a context where `Payloads` (the dictionary) is available as a variable. This means you can directly reference previously stored results without the dict name, though the example above shows the explicit form.

**Expression Evaluation Context:**
```python
# At execution time, the MethodCall is evaluated with:
Payloads = self.payloads  # Make Payloads available for eval()
# Pre-imported classes: DataProcessing, VerificationCase, Verification, Reporting
method_call = eval(self.state_dict["MethodCall"])
```

This is why `"Payloads['verification_obj'].run"` works — the `Payloads` variable is in scope during evaluation. Similarly, `"DataProcessing.add_parameter"` works without importing because the class is pre-injected into the evaluation context.

**Available Built-in Callables:**
- `DataProcessing` — data processing methods (pre-imported from `constrain.api.data_processing`)
- `VerificationCase` — verification case loading (pre-imported from `constrain.api.verification_case`)
- `Verification` — verification setup and execution (pre-imported from `constrain.api.verification`)
- `Reporting` — result reporting (pre-imported from `constrain.api.reporting`)
- `print`, `logging.error`, etc. — standard Python

#### Parameters Format

Parameters can be either:

**1. Object format (keyword arguments):**
```json
"Parameters": {
  "data_path": "./data.csv",
  "data_source": "EnergyPlus"
}
```

**2. Array format (positional arguments):**
```json
"Parameters": [
  "./demo/G36_demo/*_md.json"
]
```

**⚠️ Important:** Cannot mix keyword and positional arguments in a single state.

**Parameter Value Processing Rules:**

String parameters are processed with this logic:
- If starts with `"Payloads"` → evaluated as Python (e.g., `"Payloads['key']"`)
- If starts with `"+x "` (exactly 3 chars) → rest is evaluated (e.g., `"+x (6, 5)"` evaluates to tuple)
- Otherwise → treated as literal string

Numeric parameters (int, float) are passed through as-is. Dictionary parameters are treated as **Embedded MethodCall** states.

**Examples:**
```json
"Parameters": {
  "path": "./data.csv",                    // literal string
  "count": 42,                              // number
  "data_obj": "Payloads['processed_data']", // evaluated
  "shape": "+x (10, 5)"                    // evaluated to tuple
}
```

#### Payloads

The `Payloads` object describes how to capture and store the result of the MethodCall.

**Special Variable (`$`):**
- `"$"` represents the entire return value of the method
- Before evaluation, `"$"` is replaced with `self.dollar` (the stored return value)
- Payloads values are evaluated as Python code

**Examples of Payload Expressions:**
```json
"Payloads": {
  "entire_result": "$",                    // stores complete return
  "data_attr": "$.data",                   // equivalent to self.dollar.data
  "extracted": "$.get('key')",             // method call on return value
  "keys_list": "$.case_suite.keys()",     // chained method call
  "non_string": 42                         // non-string values stored as-is
}
```

**Important Implementation Details:**
1. Payload keys and values are evaluated at the END of the MethodCall execution
2. The `$` substitution happens before evaluation, so `"$.data"` becomes `eval("self.dollar.data")`
3. Non-string values in Payloads are stored directly without evaluation
4. Payloads are stored in a global dictionary accessible to all subsequent states via `Payloads['key_name']`

#### MethodCall State Example

```json
"load data": {
  "Type": "MethodCall",
  "MethodCall": "DataProcessing",
  "Parameters": {
    "data_path": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
    "data_source": "EnergyPlus"
  },
  "Payloads": {
    "data_processing_obj": "$",
    "data": "$.data"
  },
  "Start": "True",
  "Next": "load verification cases"
}
```

#### Embedded MethodCall

A **dict** used as a parameter value is treated as an **Embedded MethodCall** — a method call nested within a parameter. The dict must have:

```json
{
  "Type": "Embedded MethodCall",
  "MethodCall": "<python expression>",
  "Parameters": {...} or [...]
}
```

**Example Usage:**
```json
"Parameters": {
  "end_time": {
    "Type": "Embedded MethodCall",
    "MethodCall": "datetime.date.fromisoformat",
    "Parameters": {
      "date_string": "20230101"
    }
  }
}
```

This executes the embedded call first, then passes the result as the `end_time` parameter to the main MethodCall.

---

### Type 2: Choice

A **Choice** state implements conditional branching. It evaluates boolean expressions and routes to different next states based on results.

#### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `Type` | string | Must be `"Choice"` |
| `Choices` | array | Array of choice objects with `Value`, `Equals`, and `Next` |
| `Default` | string | State name to go to if no choices match |

#### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| `Start` | string | `"True"` to mark as entry point |
| `End` | string | `"True"` to mark as exit point |

#### Choice Object Structure

Each item in the `Choices` array must have:

| Property | Type | Description |
|----------|------|-------------|
| `Value` | string | Python expression that evaluates to a value |
| `Equals` | string | String representation of the expected value |
| `Next` | string | State name if condition matches |

The condition is true if `str(eval(Value)) == Equals`.

#### Choice Evaluation Rules

1. **Basic Comparison:** 
   - Both `Value` and `Equals` are evaluated if they're strings
   - Comparison is: `left == right` (Python equality)
   - The result must match for the choice to be selected

2. **Logical Expressions** (Alternative format):
   - If a choice dict has NO `"Value"` key, it's treated as a logical expression
   - Must have exactly ONE of: `"ALL"`, `"ANY"`, or `"NONE"`
   - The semantic mapping is:
     - `"ALL"` key uses `"ALL"` array → evaluates all conditions with AND logic (all must be true)
     - `"ANY"` key uses `"ANY"` array → evaluates conditions with OR logic (at least one must be true)
     - `"NONE"` key uses `"NONE"` array → evaluates conditions with NOT ANY logic (none must be true)
   - Uses leaf choice objects for sub-conditions
   - Example (ALL logic):
     ```json
     {
       "ALL": [
         {"Value": "Payloads['x']", "Equals": "True"},
         {"Value": "Payloads['y']", "Equals": "True"}
       ],
       "Next": "next_state"
     }
     ```
     This actually uses:
     ```python
     flag_list = [self.get_choice_value(x) for x in choice["ALL"]]
     choice_value = all(flag_list)  # ALL conditions must be true
     ```
   - Legacy compatibility: the runtime also accepts `"AND"` in place of `"ALL"`, but new workflows should use `"ALL"`
   - Example (ANY logic):
     ```json
     {
       "ANY": [
         {"Value": "Payloads['x']", "Equals": "True"},
         {"Value": "Payloads['y']", "Equals": "True"}
       ],
       "Next": "next_state"
     }
     ```

#### Choice State Example

```json
"check original case length": {
  "Type": "Choice",
  "Choices": [
    {
      "Value": "len(Payloads['original_case_keys']) == 3",
      "Equals": "True",
      "Next": "validate cases"
    }
  ],
  "Default": "Report Error in workflow"
}
```

---

## Control Flow

### State Transitions

States execute in sequence and form a directed graph controlled by:

1. **MethodCall states:** Next state determined by `"Next"` property
   - If `"Next"` is omitted, returns `None` (workflow terminates)
   - Execution stops unless overridden by End state logic

2. **Choice states:** Next state determined by matching conditions
   - Evaluates choices in array order
   - Returns first matching **Next** value
   - If no match, returns `"Default"` value
   - If no Default and no match, returns `None` (workflow terminates)

3. **Execution Loop:**
   - Continues while `current_state_name is not None`
   - Stops when either:
     - `current_state_name` becomes `None` (no next state)
     - Current state is marked `"End": "True"`
     - Maximum states (1000 by default) is reached

### Entry and Exit Points

- **Exactly one state** should have `"Start": "True"` — this is where execution begins
- **At least one state** should have `"End": "True"` — marks natural exit point
- Error handling: If a Choice Default leads to an error-reporting state with `"End": "True"`, error handling is explicit

### State Reachability Rules

- Every state must be reachable from the Start state
- There must be a path from Start to at least one End state
- Circular dependencies are not allowed (graph must be acyclic)
- Non-Choice states that aren't End states MUST have a `"Next"` property (enforced in `load_states()`)

---

## Payloads System

The **Payloads** dictionary is a shared store of intermediate results passed between states.

### How Payloads Work

1. **MethodCall state** stores results:
   ```json
   "Payloads": {
     "result_key": "$"  // stores the return value
   }
   ```

2. **Subsequent states** retrieve values:
   ```json
   "Parameters": {
     "data": "Payloads['result_key']"  // reference stored value
   }
   ```

3. **Choice state** evaluates conditions using Payloads:
   ```json
   "Value": "len(Payloads['data']) > 10"
   ```

### Payload Reference Syntax

| Syntax | Meaning |
|--------|---------|
| `"$"` | Store entire return value |
| `"$.attribute"` | Access attribute/key (dot notation) |
| `"$.method()"` | Call method on return value |
| `"Payloads['key']"` | Reference stored payload |
| `"+x (tuple)"` | Type hint (e.g., `"+x (6, 5)"`) |

### Payload Scope

- Payloads are **global within a single workflow execution**
- All states can access all Payloads set by previous states
- If a key is overwritten, the new value replaces the old one
- No explicit Payload cleanup between states

---

## Common Patterns

### Pattern 1: Linear Processing

```json
{
  "states": {
    "step1": {
      "Type": "MethodCall",
      "MethodCall": "Class1",
      "Parameters": {...},
      "Payloads": {"obj1": "$"},
      "Start": "True",
      "Next": "step2"
    },
    "step2": {
      "Type": "MethodCall",
      "MethodCall": "Payloads['obj1'].method",
      "Parameters": {...},
      "Payloads": {"result": "$"},
      "Next": "end"
    },
    "end": {
      "Type": "MethodCall",
      "MethodCall": "print",
      "Parameters": ["Done"],
      "End": "True"
    }
  }
}
```

### Pattern 2: Conditional Branching

```json
{
  "states": {
    "check": {
      "Type": "Choice",
      "Choices": [
        {
          "Value": "Payloads['condition']",
          "Equals": "True",
          "Next": "success_path"
        }
      ],
      "Default": "error_path"
    },
    "success_path": {
      "Type": "MethodCall",
      "MethodCall": "print",
      "Parameters": ["Success"],
      "End": "True"
    },
    "error_path": {
      "Type": "MethodCall",
      "MethodCall": "logging.error",
      "Parameters": ["Failed"],
      "End": "True"
    }
  }
}
```

### Pattern 3: Data Transformation Pipeline

```json
{
  "states": {
    "load": {
      "Type": "MethodCall",
      "MethodCall": "DataProcessing",
      "Parameters": {"data_path": "./data.csv"},
      "Payloads": {"data": "$.data"},
      "Start": "True",
      "Next": "transform"
    },
    "transform": {
      "Type": "MethodCall",
      "MethodCall": "Payloads['data'].apply",
      "Parameters": {...},
      "Payloads": {"transformed": "$"},
      "Next": "analyze"
    },
    "analyze": {
      "Type": "MethodCall",
      "MethodCall": "Verification",
      "Parameters": {"data": "Payloads['transformed']"},
      "End": "True"
    }
  }
}
```

---

## Implementation Constraints & Rules

Based on the actual implementation in `constrain/api/workflow.py`, here are enforced rules:

### State Rules
- **Non-Choice, non-End states MUST have a `Next` property** — the loader will log an error if violated
- **All state names must be unique** within a workflow—duplicates are rejected
- **Choice states must have either matching choices or a Default** — if neither, workflow returns `None` (terminates)

### MethodCall Rules
- **Parameters cannot mix keyword and positional arguments** — specify as either `{}` or `[]`, not both
- **MethodCall expression is evaluated with `Payloads` in scope** — `eval(MethodCall_string, {'Payloads': payloads_dict})`, so you can reference Payloads directly
- **Parameter processing order:**
  1. Dict parameters → treated as Embedded MethodCall (require `"Type": "Embedded MethodCall"`)
  2. String parameters starting with `"Payloads"` → evaluated
  3. String parameters starting with `"+x "` → rest evaluated
  4. Other strings → literal values
  5. Numbers → passed through

### Payload Rules  
- **Payload strings are evaluated as Python code** with `self.dollar` substituted for `$`
- **Non-string Payload values are stored as-is** without evaluation
- **Payloads are global within a workflow execution** — all states can access all previously-set Payloads
- **Payload references in Choice and MethodCall contexts** — both have `Payloads` available as a variable

### Import Rules
- **ConStrain API classes are pre-imported** — `DataProcessing`, `VerificationCase`, `Verification`, `Reporting` are automatically available
- **ConStrain imports in the imports array are auto-skipped** (to avoid redundant/invalid exec) — do not include them
- **"from X import Y" statements are executed as-is** in global scope
- **Module imports have "import" prefix auto-added if missing** to normalize syntax
- **All imports executed in global scope** at the start of workflow execution

### ConStrain API Methods — Shorthand Notation
- **Use class method directly:** `"DataProcessing.add_parameter"` instead of `"constrain.api.data_processing.DataProcessing.add_parameter"`
- **No explicit import needed** — all `constrain.api` classes are pre-injected into the MethodCall evaluation context
- **Example:** To call `constrain.api.data_processing.DataProcessing.add_parameter(...)`, use:
  ```json
  "MethodCall": "DataProcessing.add_parameter",
  "Parameters": { "name": "...", "value": ... }
  ```

### Execution Rules
- **Maximum 1000 states per workflow** (configurable, default is safety limit)
- **Original working directory is restored** after workflow completion, even on error
- **State execution is tracked** in `running_sequence` for debugging/summary

---

The workflow is validated against both:

1. **JSON Schema validation** (`constrain/schema/workflow.schema.json`):
   - Structure correctness (required fields, types)
   - Enum values (e.g., `Type` must be "MethodCall" or "Choice")
   - Conditional validation (if-then rules for MethodCall vs Choice)

2. **Runtime validation**:
   - Start/End states properly marked
   - All referenced Payloads must exist before use
   - All referenced states must exist (no dangling Next/Default references)
   - No circular dependencies in state graph

---

## Minimal Valid Workflow

```json
{
  "workflow_name": "Minimal Workflow",
  "meta": {
    "author": "User",
    "date": "03/24/2026",
    "version": "1.0",
    "description": "A minimal working workflow"
  },
  "imports": [],
  "states": {
    "start": {
      "Type": "MethodCall",
      "MethodCall": "print",
      "Parameters": ["Hello, World!"],
      "Start": "True",
      "End": "True"
    }
  }
}
```

---

## Troubleshooting Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Payload reference fails` | Key not set in previous state | Check Payloads object name matches reference |
| `Next state not found` | Typo in state name | Verify state name exists and spelling matches |
| `Type mismatch error` | Invalid Type value | Use only "MethodCall" or "Choice" |
| `Parameter evaluation fails` | Invalid Python expression | Check syntax and Payloads references |
| `Circular dependency error` | States reference each other recursively | Ensure workflow forms a DAG (directed acyclic graph) |
| `No start state` | Missing `"Start": "True"` | Mark exactly one state as entry point |
| `No end state` | Missing `"End": "True"` | Mark at least one state as exit point |

---

## Known Limitations & Gotchas

### Security Considerations
- **MethodCall and Choice expressions are evaluated with `eval()`** — user-provided workflow JSON can execute arbitrary Python
- **No sandboxing** — access to all imported modules and Python builtins
- Only use workflows from trusted sources

### String Parameter Gotchas
- **Strings starting with `"Payloads"` are ALWAYS evaluated** — if you need a literal string starting with "Payloads", this is not directly possible (use Embedded MethodCall or alternative approach)
- **Strings starting with `"+x "` are ALWAYS evaluated** — use Embedded MethodCall if you need this literal prefix
- **All other strings are treated as literals** — no variable interpolation or template substitution

### Payload Reference Gotchas
- **`$` substitution is textual** — `"$.data"` becomes `"self.dollar.data"` before evaluation, which means nested access like `"$['nested']['key']"` works but dictionary bracket notation must be on the same level
- **Payload keys are case-sensitive** — `"Payloads['Data']"` and `"Payloads['data']"` are different
- **Circular references are possible** — be careful not to store objects that reference themselves

### Execution Gotchas
- **Start state is fixed** — you cannot dynamically change which state starts the workflow
- **End state execution stops immediately** — even if the state has a `"Next"` property, it's ignored
- **Choice states that match return immediately** — subsequent choices in the array are not evaluated
- **Working directory changes are global** — all states execute in the same directory context
- **Max 1000 states is enforced** — infinite loops are caught by this hard limit

### Choice Gotchas
- **Logical expressions should use direct keys** → use `"ALL"`, `"ANY"`, and `"NONE"` with arrays of leaf predicates. The runtime still accepts legacy `"AND"` for backward compatibility, but new workflows should use `"ALL"`.
- **Choice conditions must return True/False equivalents** — string "True" vs boolean True matters for comparison
- **No partial matching** — `"Equals"` must be an exact string representation match
- **Choice evaluation is short-circuit** — first matching choice is selected; subsequent choices ignored

---

- **Workflow Schema:** `constrain/schema/workflow.schema.json`
- **Example Workflows:** `constrain/demo/*/workflow*.json`
- **API Documentation:** `constrain/api/workflow.py`
- **Runner:** `constrain/ai/workflow_runner.py`
