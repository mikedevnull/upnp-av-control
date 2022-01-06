from pytest_bdd import scenarios, when, then, parsers
from .async_utils import sync
import logging
from .common_steps import *  # noqa: F401, F403

_logger = logging.getLogger(__name__)


def find_item_with_title(payload, title):
    try:
        item = next(x for x in payload if x['title'] == title)
        return item
    except StopIteration:
        return None


scenarios('media_server_api.feature')


@when('the client requests the contents of the root element')
@sync
async def the_client_requests_the_contents_of_the_root_element(test_context, webclient):
    """the client requests the contents of the root element."""
    test_context.last_response = await webclient.get('/api/library/')
    assert test_context.last_response.status_code == 200


@when(parsers.cfparse('the client requests the contents of item {item_name}'))
@sync
async def the_client_requests_children_of_item(test_context, webclient, item_name):
    response_json = test_context.last_response.json()
    item = find_item_with_title(response_json, item_name)
    item_id = item['id']
    uri = f'/api/library/{item_id}'
    test_context.last_response = await webclient.get(uri)


@when(parsers.cfparse('the client requests the metadata of item {item_name}'))
@sync
async def the_client_requests_metadata_of_item(test_context, webclient, item_name):
    response_json = test_context.last_response.json()
    item = find_item_with_title(response_json, item_name)
    assert item is not None
    item_id = item['id']
    uri = f'/api/library/{item_id}/metadata'
    test_context.last_response = await webclient.get(uri)


@when(parsers.parse('the client requests page {pagenumber} with size {pagesize} of object FakeLongArtistListing'),
      converters=dict(pagenumber=int, pagesize=int))
@sync
async def the_client_requests_paginated(test_context, webclient, pagenumber, pagesize):

    response_json = test_context.last_response.json()
    item = find_item_with_title(response_json, "FakeLongArtistListing")
    item_id = item['id']
    browse_uri = f'/api/library/{item_id}'
    pagination_params = {'page': pagenumber, 'pagesize': pagesize}
    test_context.last_response = await webclient.get(browse_uri, query_string=pagination_params)


@then(parsers.parse('the response will contain elements from index {first_element} to index {last_element}'),
      converters=dict(first_element=int, last_element=int))
def the_response_will_contain_elements_from_index_first_element_to_index_last_element(
        test_context, first_element, last_element):
    """the response will contain elements from index <first_element> to index <last_element>."""
    assert test_context.last_response.status_code == 200
    from .fake_upnp.foo_media_server import fakeLongArtistDidl
    payload = test_context.last_response.json()
    expected = fakeLongArtistDidl[first_element:last_element + 1]
    assert len(payload) == len(expected)
    for expected_item, received_item in zip(expected, payload):
        assert 'id' in received_item
        assert received_item['title'] == expected_item.title


@then('the response will contain FooMediaServer as an entry')
def the_response_will_contain_foomediaserver(test_context):
    assert test_context.last_response.status_code == 200
    payload = test_context.last_response.json()
    device = test_context.get_device('FooMediaServer')
    item = find_item_with_title(payload, device.friendly_name)
    assert item is not None
    assert item['title'] == device.friendly_name


@then(parsers.cfparse('the response will contain the content listing of the {item} item of FooMediaServer'))
def the_response_will_contain_the_content_listing_of_item(test_context, item):
    """the response will contain the content listing of this second item."""
    if item == 'root':
        from .fake_upnp.foo_media_server import fakeRootDidl
        didl = fakeRootDidl
    elif item == 'Music':
        from .fake_upnp.foo_media_server import fakeMusicDidl
        didl = fakeMusicDidl
    assert test_context.last_response.status_code == 200
    payload = test_context.last_response.json()
    assert len(payload) == len(didl)
    for item in didl:
        other_item = find_item_with_title(payload, item.title)
        assert item.title == other_item['title']


@then('the response will contain the metadata of object Song Title 1 on FooMediaServer')
def the_response_will_contain_the_metadata_of_object_on_foomediaserver(test_context):
    """the response will contain the metadata of object SomeFakeObject on FooMediaServer."""
    from .fake_upnp.foo_media_server import fakeMusicDidl
    assert test_context.last_response.status_code == 200
    didl = fakeMusicDidl[0]
    payload = test_context.last_response.json()
    assert 'id' in payload  # not equal to original didl, rewritten by frontend
    assert 'parentID' in payload  # not equal to original didl, rewritten by frontend
    assert payload['upnpclass'] == didl.upnpclass
    assert payload['title'] == didl.title
    assert payload['album'] == didl.album
    assert payload['artist'] == didl.artist
    assert payload['originalTrackNumber'] == didl.originalTrackNumber
