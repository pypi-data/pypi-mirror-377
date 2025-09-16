from mast_aladin import MastAladin


def test_instance_creation(MastAladin_app):
    assert isinstance(MastAladin_app, MastAladin)
