# Building a ZnTrack Workflow

This guide outlines the steps and best practices for constructing a computational workflow using ZnTrack.

**READ THE FOLLOWING CAREFULLY AND FOLLOW THE INSTRUCTIONS!**

Follow these steps to define your workflow graph in a Python script (e.g., `<project-name>/main.py`).

1. **Identify which nodes you need and how you want to connect them.**
2.  **Import and instantiate `zntrack.Project`**.
3.  **Define nodes inside the `with project:` context manager**. All computational steps must be defined here.
4.  **(Optional) Organize nodes** using `with project.group("group-name"):` for complex workflows.
5.  **Connect nodes** by assigning the output attribute of one node to the input attribute of another inside the constructor (e.g., `node2 = Node(input=node1.output)`).
6.  **Build the project** by calling `project.build()` inside an `if __name__ == "__main__":` block.
7. **(Optional) Inspect the graph** using `uv run main.py` followed by `uv run dvc dag --mermaid`.

### Basic Example

```python
import zntrack
from package import Node1, Node2

project = zntrack.Project()

with project:
    # Define nodes inside the context
    node1 = Node1(param="value1")
    # Connect nodes using their attributes
    node2 = Node2(input=node1.output)

if __name__ == "__main__":
    project.build() # Build the graph
```

## 3. Important Rules

> [!WARNING]
> Pay close attention to these critical rules to avoid common errors.
>
> 1.  **Connect ONLY Nodes**: You can only connect node attributes to other node attributes. **Never pass a regular Python object as an input to a node**.
> 2.  **Use the Context Manager**: All nodes that are part of the computational graph **must be defined within a `with project:` or `with project.group(...)` block**.
>       * If `node=False` the obj is purely a parameter container for another node. It can and often should be defined outside the context manager! There should be no context manager purely for `node=False` objects.
> 3.  **Valid Group Names**: Group names can **only contain alphanumeric characters and hyphens (`-`)**.

## 4. Best Practices

Optimize your workflow for clarity and efficiency.

### Reuse Nodes to Avoid Duplication

**Don't** redefine the same node in multiple groups. This causes it to run multiple times.

```python
# Don't do this!
with project.group("a"):
    node1 = Node1(param="value1") # Runs once
    node2 = Node2(input=node1.output)
with project.group("b"):
    node1 = Node1(param="value1") # Runs a second time!
    node3 = Node3(input=node1.output)
```

**Do** define a node once and reference it in other parts of the workflow.

```python
# Do this!
with project:
    node1 = Node1(param="value1") # Runs only once

with project.group("a"):
    node2 = Node2(input=node1.output)
with project.group("b"):
    node3 = Node3(input=node1.output)
```

### Use Loops for Repetitive Tasks

**Don't** manually create nodes that follow a simple pattern.

```python
# Don't do this!
with project.group("param-1"):
    node1 = Node1(param=1)
with project.group("param-2"):
    node1 = Node1(param=2)
```

**Do** use a `for` loop to generate them programmatically.

```python
# Do this!
for i in range(1, 3):
    with project.group(f"param-{i}"): # Ensure group name is valid
        node1 = Node1(param=i)
```

## Use groups and custom node names
Use group and nested groups to organize your workflow.
Use custom node-names when appropriate to improve readability, but prefer the default names and groups!
Node names can not be duplicated within the same group! Node names can only contain alphanumeric characters and hyphens (`-`).

```python
with project.group("data", "preprocessing"):
    data = ips.AddData(file="...") # do not name this e.g. name="adding-data
with project.group("data", "split"):
    train = ips.RandomSelection(
        data=data.frames, n_configurations=100, name="train"
    ) # would be named RandomSelection
    test = ips.RandomSelection(
        data=train.excluded_frames, n_configurations=100, name="test"
    ) # would be named RandomSelection_1
```
