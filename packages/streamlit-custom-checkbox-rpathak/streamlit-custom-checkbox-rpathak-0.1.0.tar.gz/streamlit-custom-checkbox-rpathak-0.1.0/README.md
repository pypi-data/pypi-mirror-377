# Streamlit Custom Checkbox

A custom checkbox component for Streamlit with enhanced styling.

## Installation

```bash
pip install streamlit-custom-checkbox-rpathak
```

## Usage

```python
import streamlit as st
from streamlit_custom_checkbox import st_custom_checkbox

# Basic usage
result = st_custom_checkbox("Approve Document")

# With initial value
result = st_custom_checkbox("Enable Feature", value=True)

# Disabled checkbox
result = st_custom_checkbox("Disabled Option", disabled=True)
```

## Development

To build the frontend:

```bash
cd streamlit_custom_checkbox/frontend
npm install
npm run build
```

## Features

- Custom styling with green accent color
- Dynamic border and background color changes
- Support for disabled state
- Proper Streamlit integration