from docx import Document
from docx.oxml.ns import qn
from docx.text.run import Run
from sys import argv, stderr
from os.path import isfile

tab = qn("w:tab")


def extract_paragraph(paragraph):
    p = paragraph._element
    # ---use XPath to get all the w:r descendents, wherever they may be---
    rs = p.xpath(".//w:r")
    # ---generate a Run object for each w:r element, in document order---
    # for r in rs:
    txt = "".join(["\t" if r.tag == tab else r.text for r in rs])
    return txt


def extract_text_from_docx(
    filename, start_text="-- ASN1START", stop_text="-- ASN1STOP", add=False
):
    """extract asn1 from a docx file"""
    if not isfile(filename):
        print(f"File {filename} not found", file=stderr)
        return None
    doc = Document(filename)
    full_text = []
    inside_range = False
    for para in doc.paragraphs:
        text = extract_paragraph(para)
        if text.startswith(start_text):
            if add:
                full_text.append(text)
            inside_range = True
            continue
        elif text.startswith(stop_text):
            if add:
                full_text.append(text)
            inside_range = False
            continue

        # Add the paragraph text if inside the desired range
        if inside_range:
            full_text.append(text)
    return "\n".join(full_text)


def main():
    """main function"""
    if len(argv) < 2:
        print("Usage: python decode_asn1.py <filename>", file=stderr)
        print("Or: python decode_asn1.py <filename> <outputfile>", file=stderr)
        return
    extracted_text = extract_text_from_docx(argv[1])
    if extracted_text is None:
        return
    if len(argv) > 2:
        output_filename = argv[2]
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(extracted_text)
    else:
        print(extracted_text)
