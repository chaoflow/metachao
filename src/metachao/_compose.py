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
            if name in dct:
                instr = instr.compose(dct[name])
            dct[name] = instr

        name = "Composition"
        bases = ()
        composition = aspect.__class__(name, bases, dct)

    return composition
