import re


codes = [
    (r'(?:astro-ph|cond-mat|cs|gr-qc|hep-ex|hep-lat|hep-ph|hep-th|math|math-ph|nlin|nucl-ex|nucl-th|physics|q-bio|q-fin|quant-ph|stat)(?:\.[a-zA-Z-]+)*',
     'arxiv'),
    (r'[0-9]{2,2}[A-Z][0-9]{2,2}', 'MSC'),
    (r'[A-Z](?:\.[0-9m]){1,2}', 'ACM'),
]

def classify(codes):
    """Put classification codes into gropus."""
    categories = {}

    for code in codes:
        match = False
        for group in codes:
            matches = re.findall(group[0], code)
            if matches:
                categories.setdefault(group[1], []).extend(matches)
                match = True
        if not match:
            categories.setdefault('unknown', []).append(code)
    return categories
