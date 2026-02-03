from biometaprep.normalize.clean import _canonicalize_organism

def test_canonicalize_human():
    assert _canonicalize_organism("human") == "Homo sapiens"

def test_canonicalize_mouse():
    assert _canonicalize_organism("mouse") == "Mus musculus"