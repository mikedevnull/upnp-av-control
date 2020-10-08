import utils from '../container-type-utils';

describe('imageForItem', () => {
  it('should use albumArtURI with api prefix if available', () => {
    const testItem = { upnpclass: 'object.container.person.musicArtist', albumArtURI: "/foo" }
    let result = utils.imageForItem(testItem);
    expect(result).toBe('/api/foo');
  })
  it('should use artistDiscographyURI with api prefix if available', () => {
    const testItem = { upnpclass: 'object.container.person.musicArtist', artistDiscographyURI: "/bar" }
    let result = utils.imageForItem(testItem);
    expect(result).toBe('/api/bar');
  })

  it('should map musicArtist upnpclass to correct svg', () => {
    const testItem = { upnpclass: 'object.container.person.musicArtist' }
    let result = utils.imageForItem(testItem);
    expect(result).toEqual(utils.personIcon);
  })

  it('should map musicAlbum upnpclass to correct svg', () => {
    const testItem = { upnpclass: 'object.container.album.musicAlbum' }
    let result = utils.imageForItem(testItem);
    expect(result).toEqual(utils.albumIcon);
  })

  it('should map musicTrack upnpclass to correct svg', () => {
    const testItem = { upnpclass: 'object.item.audioItem.musicTrack' }
    let result = utils.imageForItem(testItem);
    expect(result).toEqual(utils.trackIcon);
  })

  it('should map unkown upnpclasses to a fallback svg', () => {
    const testItem = { upnpclass: 'object.item.photoItem' }
    let result = utils.imageForItem(testItem);
    expect(result).toEqual(utils.fallbackIcon);
  })
})

describe('itemBrowseChildrenRoute', () => {
  it('should format a correct route definition', () => {
    let result = utils.itemBrowseChildrenRoute('1234-5678', 'foo')
    expect(result).toEqual({ name: "browse", params: { udn: '1234-5678' }, query: { objectID: 'foo' } })
  })
})

describe('filterByUpnpClass', () => {
  it('should filter items by upnpclass', () => {
    let items = [{ name: 'foo', upnpclass: 'object.container.album.musicAlbum' },
    { name: 'item2', upnpclass: 'object.item.audioItem' },
    { name: 'item42', upnpclass: 'object.container.album.fooBar' },
    { name: 'noname', upnpclass: 'object.container.playlist' }]
    let expectResult = [items[0], items[2]];
    let result = utils.filterByUpnpClass(items, 'object.container.album');
    expect(result).toEqual(expectResult);
  })

  it('should return an empty list for undefined input', () => {
    let result = utils.filterByUpnpClass(undefined, 'foo.bar')
    expect(result.length).toBe(0);
  })
})

describe('guessImageForParentItem', () => {
  const children = [{}, { albumArtURI: '/bar' }]
  it('should return item albumArt if available', () => {
    let item = { albumArtURI: '/foo' }
    let result = utils.guessImageForParentItem(item, children);
    expect(result).toBe(utils.imageForItem(item));
  })

  it('should return item artistDiscography if available', () => {
    let item = { artistDiscographyURI: '/foo' }
    let result = utils.guessImageForParentItem(item, children);
    expect(result).toBe(utils.imageForItem(item));
  })

  it('should return child image if available', () => {
    let item = {}
    let result = utils.guessImageForParentItem(item, children);
    expect(result).toBe(utils.imageForItem(children[1]));
  })

  it('should return default icon as fallback', () => {
    let item = { upnpclass: 'object.unkown' }
    let result = utils.guessImageForParentItem(item, [{}]);
    expect(result).toBe(utils.imageForItem(item));
  })

  it('should work with undefined children', () => {
    let item = { upnpclass: 'object.unkown' }
    let result = utils.guessImageForParentItem(item);
    expect(result).toBe(utils.imageForItem(item));
  })

  it('should work with undefined item', () => {
    let result = utils.guessImageForParentItem();
    expect(result).toBe(utils.fallbackIcon);
  })
})
