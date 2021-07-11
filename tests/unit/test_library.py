import pytest
from upnpavcontrol.web.api.library import create_library_item_id, split_library_item_id


@pytest.mark.asyncio
@pytest.mark.parametrize("udn, objectID",
                         [('10-20-30', '0'), ('10-20-30', '/foo/bar/baz'), ('10-20-30', '/foo/bar.baz'),
                          ('10-20-30', None), ('10-20-30', '/foo/bar.baz'), ('10-20-30', '')])
async def test_encode_decode_library_item(udn, objectID):
    encoded = create_library_item_id(udn, objectID)
    decoded_udn, decoded_objectID = split_library_item_id(encoded)
    assert decoded_udn == udn
    assert decoded_objectID == objectID
