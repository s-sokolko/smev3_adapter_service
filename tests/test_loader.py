import pytest
from smev_int.schema_loader.loader import Loader
from zeep import xsd
from lxml import etree
import smev_int.schema_loader.transport as transport


def test_load(mocker):
    mocker.patch('smev_int.schema_loader.loader.Loader.list_dirs', new=mocker.MagicMock(return_value=['fakedir']))
    mocker.patch('smev_int.schema_loader.loader.Loader.list_files', new=mocker.MagicMock(return_value=['fakefile']))
    mocker.patch('lxml.etree.parse')
    mocker.patch('smev_int.schema_loader.transport.Transport')
    mocker.patch('zeep.xsd.Schema')
    l = Loader()
    l.list_dirs.assert_called_once_with(l._path)
    l.list_files.assert_called_once_with('fakedir')
    etree.parse.assert_called_once_with('fakefile')
    transport.Transport.assert_not_called()
    xsd.Schema.assert_any_call()


@pytest.mark.parametrize("se,expected", [
    (Exception('No luck'), None),
    ([Exception('No luck'), Exception('No luck'), 'Bingo'], 'Bingo'),
])
def test_get_element(mocker, se, expected):
    schema = mocker.MagicMock()
    schema.namespaces = ['a', 'b', 'c']
    schema.get_element = mocker.MagicMock(side_effect=se)
    mocker.patch('smev_int.schema_loader.loader.Loader.load')
    l = Loader()
    mocker.patch.object(l, 'schema', new=schema)
    el = l.get_element('Abracadabra')
    schema.get_element.assert_has_calls([mocker.call('{a}Abracadabra'),
                                         mocker.call('{b}Abracadabra'),
                                         mocker.call('{c}Abracadabra')])
    assert el == expected


@pytest.mark.parametrize("element", [
    'FNSVipULRequest',
    'FNSVipULResponse',
    'FNSVipIPRequest',
    'FNSVipIPResponse'
])
def test_loader_integration(element):
    from importlib import reload
    import smev_int.schema_loader.loader
    reload(smev_int.schema_loader.loader)
    l = smev_int.schema_loader.loader.Loader()
    req = l.get_element(element)
    assert req is not None