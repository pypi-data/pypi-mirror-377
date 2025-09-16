# CyVer

<div align="center">
    <img src="https://gitlab.com/netmode/CyVer/-/raw/main/materials/logoCyVer.jpg?ref_type=heads" alt="CyVer" width="300">
</div>

<div align="center">
  <b>Syntax, Schema And Property Access Validation of Cypher queries</b>
</div>

<div align="center">

[![License](https://img.shields.io/badge/License-CC_BY_SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-brightgreen)](https://www.python.org/)[![Documentation](https://img.shields.io/badge/Documentation-online-orange)](https://gitlab.com/netmode/CyVer/-/wikis/home)[![Cite](https://img.shields.io/badge/Cite%20as-doi-yellow)](https://ieeexplore.ieee.org/document/10990239)

</div>

**CyVer** is a Python library designed to validate Cypher queries against a given Knowledge Graph schema in Neo4j. It ensures correctness in terms of syntax, schema validity, and property access.

## Features

* **Syntax Validation**: Validates Cypher queries for correct syntax and detects conflicting labels in nodes and relationships.
* **Schema Validation**: Checks query alignment with a predefined KG schema structure.
* **Property Validation**: Ensures property accesses are correct based on the predefined KG schema structure.

### New Feature in release v2.x:

* **Validators Metadata Reporting**: Alongside validation results, CyVer returns detailed metadata describing each detected issue in a Cypher query — including the type of error, its location, and suggestions for how to fix it.

## 📖 Documentation

For documentation read [Wiki](https://gitlab.com/netmode/CyVer/-/wikis/home).

## 📋 Requirements

Before installing, make sure you have the following Python packages installed, with Python version >= 3.10:

* regex>=2024.11.6
* neo4j>=5.27
* pandas>=2.2.3

## 📦 Installation

To install the latest stable version from [PyPI](https://pypi.org/project/CyVer/), run:

```sh
pip install CyVer
```

Alternatively, if you prefer to install the latest development version, you can install it directly from GitLab:

```sh
pip install git+https://gitlab.com/netmode/CyVer.git
```

Or, you can manually clone the repository and run:

```sh
git clone https://gitlab.com/netmode/CyVer.git
cd CyVer
pip install .
```

## 💻 Example Usage

### Importing the Library

```sh
from CyVer import SyntaxValidator, SchemaValidator, PropertiesValidator
```

### Connect to Neo4j Database instance

```sh
from neo4j import GraphDatabase,basic_auth

driver = GraphDatabase.driver(database_url, auth=basic_auth(database_username, database_password))
```

### Syntax Validator

```sh
syntax_validator =  SyntaxValidator(driver, check_multilabeled_nodes=False)
query = 'MATCH (g:Goal) RETURN COUNT(g) AS output'
is_valid, syntax_metadata = syntax_validator.validate(query, database_name=database_name)
print(f"Syntax Valid: {is_valid}")
print(f"Syntax Metadata: {syntax_metadata}")
```

### Schema Validator

```sh
schema_validator =  SchemaValidator(driver)
query = 'MATCH (g:Goal)-[:HAS_TARGET]->(t:Target) RETURN g, t'
# Extraction
extracted_node_labels, extracted_rel_labels, extracted_paths = schema_validator.extract(query, database_name=database_name)
print(f"Extracted Node patterns : {extracted_node_labels}")
print(f"Extracted Relationships patterns : {extracted_rel_labels}")
print(f"Extracted Path patterns : {extracted_paths}")
# Validation 
schema_score, schema_metadata = schema_validator.validate(query, database_name=database_name)
print(f"Schema Validation Score: {schema_score}")
print(f"Schema Validation Metadata: {schema_metadata}")

```

### Properties Validator

```sh
props_validator =  PropertiesValidator(driver)
query = 'MATCH (g:Goal)-[:HAS_TARGET]-(t:Target) WHERE g.code =1 RETURN t'
# Extraction
variables_properties , labels_properties = props_validator.extract(query, strict = False, database_name=database_name)
print(f"Accessed properties by variables: {variables_properties}")
print(f"Accessed properties by labels (including inferred): {labels_properties}")

# Validation 
props_score, properties_metadata = props_validator.validate(query, database_name=database_name, strict=False)
print(f"Properties Validation Score: {props_score}")
print(f"Properties Validation Metadata: {properties_metadata}")

```

## 📊 **Tip:**

> Always start with the **SyntaxValidator** before using the **Schema** and *Properties* validators. Even a small syntax error can cause misleading results in downstream validation. Ensuring syntactic correctness first helps you avoid wasted time and confusion. Building on this principle, we define the KG Valid Query metric to systematically evaluate generated Cypher queries for knowledge graphs.

A query is considered valid only if it satisfies all three checks:

1. SyntaxValidator.is_valid= True → the query is syntactically correct.
2. SchemaValidator.score = 1 → the query respects the graph schema.
3. PropertiesValidator.score = 1 or None → the query accesses only valid properties.

<div align="center">
    <img src="https://gitlab.com/netmode/CyVer/-/raw/main/materials/KG_Valid_Query.jpg" alt="KG_Valid_Query">
</div>

## License

This project is licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license.

## 🤝 Contributing

Contributions are welcome! Please submit a pull request or open an issue.

## Cite

To cite this work, please use:

I. Mandilara, C. M. Androna, E. Fotopoulou, A. Zafeiropoulos and S. Papavassiliou, "Decoding the Mystery: How can LLMs Turn Text into Cypher in Complex Knowledge Graphs?," in  *IEEE Access* , doi: [10.1109/ACCESS.2025.3567759](https://ieeexplore.ieee.org/document/10990239).

## Contact

For any request for detailed information or expression of interest for participating at this initiative, you may contact:

- Ioanna Mandilara - ioannamand (at) netmode (dot) ntua (dot) gr
- Christina Maria Androna - andronaxm (at) netmode (dot) ntua (dot) gr

---
