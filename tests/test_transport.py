import pytest
import os

from smev_int.schema_loader.transport import Transport


@pytest.mark.parametrize("fname", ['xsd/15980', 'xsd/34087'])
def test_transport_load(fname):
    t = Transport(fname)
    for f in os.listdir(fname):
        name = os.path.join(fname, f)
        if os.path.isfile(name):
            data = t.load(f)
            with open(name, 'rb') as handle:
                expected_data = handle.read()
            assert data == expected_data
