from pytest_bdd import scenarios, when, then, scenario, parsers
from .async_utils import sync
import logging
from .common_steps import *  # noqa: F401, F403

_logger = logging.getLogger(__name__)


@scenario("media_server_api.feature", "Pagination", example_converters=dict(first_element=int, last_element=int))
def test_browse_pagination():
    pass


scenarios('media_server_api.feature')


@when('the client requests the contents of the root element')
@sync
async def the_client_requests_the_contents_of_the_root_element(test_context, webclient):
    """the client requests the contents of the root element."""
    device_name = 'FooMediaServer'
    device = test_context.get_device(device_name)
    udn = device.udn
    browse_uri = await get_browse_path(webclient, udn)
    test_context.last_response = await webclient.get(browse_uri)
    assert test_context.last_response.status_code == 200


@when('the client requests link of the second item in the response')
@sync
async def the_client_requests_link_of_the_second_in_the_response(test_context, webclient):
    """the client requests link of the second in the response."""
    response_json = test_context.last_response.json()
    second_item = response_json['data'][1]
    browse_uri = extract_browse_path(second_item)
    test_context.last_response = await webclient.get(browse_uri)


@when('the client requests page <pagenumber> with size <pagesize> of object FakeLongArtistListing')
@sync
async def the_client_requests_paginated(test_context, webclient, pagenumber, pagesize):
    """the client requests page <pagenumber> with size <pagesize> of object FakeLongArtistListing."""
    device_name = 'FooMediaServer'
    device = test_context.get_device(device_name)
    udn = device.udn
    browse_uri = await get_browse_path(webclient, udn)
    pagination_params = {'page': pagenumber, 'pagesize': pagesize, 'objectID': 'FakeLongArtistListing'}
    test_context.last_response = await webclient.get(browse_uri, query_string=pagination_params)


@when('the client requests the object metadata of object SomeFakeObject on FooMediaServer')
@sync
async def the_client_requests_the_object_metadata_on_foomediaserver(test_context, webclient):
    """the client requests the object metadata of object SomeFakeObject on FooMediaServer."""
    device_name = 'FooMediaServer'
    device = test_context.get_device(device_name)
    udn = device.udn
    browse_uri = await get_metadata_path(webclient, udn)
    test_context.last_response = await webclient.get(browse_uri, query_string={'objectID': 'SomeFakeObject'})


@then(parsers.cfparse('the response will contain elements from index <first_element> to index <last_element>'))
def the_response_will_contain_elements_from_index_first_element_to_index_last_element(
        test_context, first_element, last_element):
    """the response will contain elements from index <first_element> to index <last_element>."""
    assert test_context.last_response.status_code == 200
    from .fake_upnp.foo_media_server import fakeLongArtistDidl
    payload = test_context.last_response.json()
    expected = fakeLongArtistDidl[first_element:last_element + 1]
    assert len(payload['data']) == len(expected)
    for expected_item, received_item in zip(expected, payload['data']):
        assert received_item['id'] == expected_item.id
        assert received_item['attributes']['title'] == expected_item.title
        assert received_item['attributes']['album'] == expected_item.album
        assert received_item['attributes']['artist'] == expected_item.artist


@then('the response will contain the content listing of this second item')
def the_response_will_contain_the_content_listing_of_this_second_item(test_context):
    """the response will contain the content listing of this second item."""
    from .fake_upnp.foo_media_server import fakeMusicDidl
    assert test_context.last_response.status_code == 200
    payload = test_context.last_response.json()
    assert len(payload['data']) == len(fakeMusicDidl)
    data0 = payload['data'][0]
    assert data0['attributes']['title'] == fakeMusicDidl[0].title
    assert data0['attributes']['album'] == fakeMusicDidl[0].album
    assert data0['attributes']['artist'] == fakeMusicDidl[0].artist
    assert data0['id'] == fakeMusicDidl[0].id

    data1 = payload['data'][1]
    assert data1['attributes']['title'] == fakeMusicDidl[1].title
    assert data1['attributes']['album'] == fakeMusicDidl[1].album
    assert data1['attributes']['artist'] == fakeMusicDidl[1].artist
    assert data1['id'] == fakeMusicDidl[1].id


@then('the response will contain the metadata of object SomeFakeObject on FooMediaServer')
def the_response_will_contain_the_metadata_of_object_on_foomediaserver(test_context):
    """the response will contain the metadata of object SomeFakeObject on FooMediaServer."""
    from .fake_upnp.foo_media_server import someFakeObjectDidlMetadata
    assert test_context.last_response.status_code == 200
    payload = test_context.last_response.json()
    _logger.debug(payload)
    attributes = payload['data']['attributes']
    assert attributes['id'] == someFakeObjectDidlMetadata.id
    assert attributes['parentID'] == someFakeObjectDidlMetadata.parentID
    assert attributes['upnpclass'] == someFakeObjectDidlMetadata.upnpclass
    assert attributes['title'] == someFakeObjectDidlMetadata.title
    assert attributes['album'] == someFakeObjectDidlMetadata.album
    assert attributes['artist'] == someFakeObjectDidlMetadata.artist
    assert attributes['originalTrackNumber'] == someFakeObjectDidlMetadata.originalTrackNumber
