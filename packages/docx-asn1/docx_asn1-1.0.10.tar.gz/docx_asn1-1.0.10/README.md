# docx-asn1 [![version](https://img.shields.io/pypi/v/docx-asn1)](https://pypi.org/project/docx-asn1/)

Decode `asn1` from a docx file. Question for @3gpp: why `docx` from for the specification ?

## CLI

```sh
# download the docx
python -m pip install docx_asn1
python -m docx_asn1 file.docx output.asn1
# or
python -m docx_asn1 file.docx > output.asn1
```

## Python usage

```python
from docx_asn1 import extract_text_from_docx

asn1 = extract_text_from_docx("file.docx")
```
