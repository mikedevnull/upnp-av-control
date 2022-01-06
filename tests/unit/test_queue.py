import pytest
from upnpavcontrol.core.playback.queue import PlaybackQueue


@pytest.fixture
def queue_with_items():
    queue = PlaybackQueue()
    queue.append(dms='1234', object_id='9876', title='First song')
    queue.append(dms='56789', object_id='54321', title='Second song')
    return queue


@pytest.mark.asyncio
async def test_empty_queue():
    queue = PlaybackQueue()

    assert queue.current_item is None
    assert len(queue.items) == 0


@pytest.mark.asyncio
async def test_next_item_steps_trough_queue(queue_with_items):
    assert len(queue_with_items.items) == 2
    item = queue_with_items.next_item()

    assert item.dms == '1234'
    assert item.object_id == '9876'
    assert item.title == 'First song'

    assert len(queue_with_items.items) == 2
    assert queue_with_items.current_item_index == 0

    item = queue_with_items.next_item()

    assert item.dms == '56789'
    assert item.object_id == '54321'
    assert item.title == 'Second song'

    assert len(queue_with_items.items) == 2
    assert queue_with_items.current_item_index == 1

    item = queue_with_items.next_item()

    assert item is None
    assert len(queue_with_items.items) == 2
    assert queue_with_items.current_item_index is None


@pytest.mark.asyncio
async def test_queue_clear(queue_with_items):
    item = queue_with_items.next_item()
    assert item is not None

    queue_with_items.clear()

    assert queue_with_items.current_item is None
    assert queue_with_items.current_item_index is None
    assert len(queue_with_items.items) == 0
