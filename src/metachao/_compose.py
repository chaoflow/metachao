def compose(*aspects):
    """Create a composite aspect from a list of aspects
    """
    aspects = list(aspects)
    composition = aspects.pop()
    while aspects:
        composition = aspects.pop()(composition)
    return composition
