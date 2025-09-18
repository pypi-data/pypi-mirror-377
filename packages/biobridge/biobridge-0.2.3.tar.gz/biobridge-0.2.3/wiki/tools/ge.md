# GelElectrophoresis Class

---

## Overview
The `GelElectrophoresis` class simulates the process of gel electrophoresis, a technique used to separate DNA fragments based on their size. The class allows loading DNA samples, running the electrophoresis process, and visualizing the results.

---

## Class Definition

```python
class GelElectrophoresis:
    def __init__(self, gel_length: int = 100, voltage: float = 100.0):
        """
        Initialize a new GelElectrophoresis object.
        :param gel_length: Length of the gel in arbitrary units (default: 100)
        :param voltage: Voltage applied during electrophoresis (default: 100.0)
        """
        ...
```

---

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `gel_length` | `int` | Length of the gel in arbitrary units. |
| `voltage` | `float` | Voltage applied during electrophoresis. |
| `samples` | `List[DNA]` | List of DNA samples loaded into the gel. |

---

## Methods

### Initialization
- **`__init__(self, gel_length: int = 100, voltage: float = 100.0)`**
  Initializes a new `GelElectrophoresis` instance with the specified gel length and voltage.

---

### Sample Loading
- **`load_sample(self, dna: DNA)`**
  Loads a DNA sample into the gel.

  - **Parameters**:
    - `dna`: The DNA object to load into the gel.

---

### Electrophoresis Process
- **`run_electrophoresis(self, duration: float) -> List[Tuple[DNA, int]]`**
  Simulates the electrophoresis process.

  - **Parameters**:
    - `duration`: The duration of the electrophoresis in minutes.

  - **Returns**: A list of tuples containing the DNA samples and their positions on the gel, sorted by migration distance.

  - **Details**:
    - The migration distance is calculated based on the DNA length, voltage, and duration.
    - Shorter DNA fragments migrate further than longer fragments.

---

### Visualization
- **`visualize_results(self, results: List[Tuple[DNA, int]])`**
  Creates a simple ASCII visualization of the gel electrophoresis results.

  - **Parameters**:
    - `results`: List of tuples containing the DNA samples and their positions on the gel.

  - **Details**:
    - The visualization shows each DNA sample's position on the gel.
    - The length of each DNA fragment is displayed in base pairs (bp).

---

## Example Usage

```python
# Initialize the GelElectrophoresis
gel = GelElectrophoresis(gel_length=100, voltage=100.0)

# Create DNA samples
dna1 = DNA(sequence="ATGCGATCG")
dna2 = DNA(sequence="ATGCGATCGATCGATCGATCG")
dna3 = DNA(sequence="ATGCGATCGATCGATCGATCGATCGATCGATCG")

# Load DNA samples into the gel
gel.load_sample(dna1)
gel.load_sample(dna2)
gel.load_sample(dna3)

# Run electrophoresis
results = gel.run_electrophoresis(duration=30.0)

# Visualize the results
gel.visualize_results(results)
```

---

## Expected Output

```
Gel Electrophoresis Results:
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|                                                                                                    |
|                                      8bp                                                          |
|                                                                                                    |
|                              16bp                                                                   |
|                                                                                                    |
|                                                                     24bp                          |
+----------------------------------------------------------------------------------------------------+
  012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
```

---

## Dependencies
- **`DNA`**: Class representing DNA sequences.

---

## Error Handling
- The class does not explicitly handle errors, but it includes checks to ensure migration distances do not exceed the gel length.

---

## Notes
- The `GelElectrophoresis` class is designed to simulate the basic principles of gel electrophoresis.
- The migration distance is inversely proportional to the square root of the DNA length, reflecting the real-world behavior of DNA fragments in a gel.
- The `visualize_results` method provides a simple ASCII representation of the gel, showing the relative positions of DNA fragments.
