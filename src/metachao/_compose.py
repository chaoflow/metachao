class _UNSET:
    pass


def compose(*aspects):
    """Create a composite aspect from a list of aspects
    """
    aspects = list(aspects)
    composition = aspects.pop()
    while aspects:
        aspect = aspects.pop()

        dct = dict()
        dct.update(composition.__metachao_instructions__)
        for name, instr in aspect.__metachao_instructions__.items():
            existing = dct.get(name, _UNSET)
            if existing is not _UNSET:
                instr = instr.compose(existing)
            dct[name] = instr

        name = "Composition"
        bases = ()
        composition = aspect.__class__(name, bases, dct)

    return composition
