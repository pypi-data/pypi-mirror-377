# faker_researcher_ids

A Python package extending `Faker` to generate fake author identifiers used in scientific databases and publication tracking systems:
- Scopus;
- ORCID;
- Web of Science;
- Google Scholar.

## Installation

Install with `pip`:  
```bash
pip install faker_researcher_ids
```

Or with `uv`:  
```bash
uv add faker_researcher_ids
```

## Usage

1. Import necessary dependencies:  
```python
from faker import Faker  
from faker_researcher_ids import ScientificProvider
```

2. Create a `Faker` instance:
```python
fake = Faker()
```

3. Add the provider to created instance:
```python
fake.add_provider(ScientificProvider)
```

### Identifiers generation

```python
# Scopus Author ID
>>> fake.scopus_id()
'53070267764'

# Web of Science ID (aka ResearcherID)
>>> fake.wos_id()
'O-2416-2014'

# ORCID
>>> fake.orcid()
'https://orcid.org/0009-0008-7383-0730'

# Google Scholar ID
>>> fake.google_scholar_id()
'ogf35PW74DCe'
```