import { enableAutoDestroy, shallowMount, mount, RouterLinkStub } from '@vue/test-utils'
import MediaserverBrowser from '@/pages/MediaserverBrowser';
import ArtistBrowser from '@/pages/MediaserverBrowser/ArtistBrowser';
import AlbumBrowser from '@/pages/MediaserverBrowser/AlbumBrowser';
import GenericContainerBrowser from '@/pages/MediaserverBrowser/GenericContainerBrowser';
import TrackList from '@/pages/MediaserverBrowser/TrackList';
import CoverImageGrid from '@/pages/MediaserverBrowser/CoverImageGrid';

jest.mock('@/upnpapi')
import ControlPoint from '@/upnpapi';
import ContainerBrowserMixin from '../ContainerBrowserMixin';

enableAutoDestroy(afterEach)

describe('MediaserverBrowser.vue', () => {

  it('should show a generic container listing for containers', async () => {
    ControlPoint.getObjectMetadata.mockResolvedValueOnce([{ id: '123', title: 'foo', upnpclass: 'object.container.foo.bar' }])
    let wrapper = shallowMount(MediaserverBrowser)
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.ready).toBeTruthy();
    expect(wrapper.vm.title).toBe('foo');
    expect(wrapper.vm.browseComponent).toBe(GenericContainerBrowser);
  })

  it('should show the album view for album containers', async () => {
    ControlPoint.getObjectMetadata.mockResolvedValueOnce([{ id: '123', title: 'foo', upnpclass: 'object.container.album.musicAlbum' }])
    let wrapper = shallowMount(MediaserverBrowser)
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.ready).toBeTruthy();
    expect(wrapper.vm.title).toBe('foo');
    expect(wrapper.vm.browseComponent).toBe(AlbumBrowser);
  })

  it('should show the artist view for artist containers', async () => {
    ControlPoint.getObjectMetadata.mockResolvedValueOnce([{ id: '123', title: 'foo', upnpclass: 'object.container.person.musicArtist' }])
    let wrapper = shallowMount(MediaserverBrowser)
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.ready).toBeTruthy()
    expect(wrapper.vm.title).toBe('foo');
    expect(wrapper.vm.browseComponent).toBe(ArtistBrowser);
  })

  it('should reload on property change and adjust the subview', async () => {
    ControlPoint.getObjectMetadata.mockResolvedValueOnce([{ id: '123', title: 'foo', upnpclass: 'object.container.person.musicArtist' }])
    ControlPoint.getObjectMetadata.mockResolvedValueOnce([{ id: '456', title: 'bar', upnpclass: 'object.container.album.musicAlbum' }])
    let wrapper = shallowMount(MediaserverBrowser)
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.ready).toBeTruthy();
    expect(wrapper.vm.title).toBe('foo');
    expect(wrapper.vm.browseComponent).toBe(ArtistBrowser);

    wrapper.setProps({ objectID: '456' });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.ready).toBeTruthy();
    expect(wrapper.vm.title).toBe('bar');
    expect(wrapper.vm.browseComponent).toBe(AlbumBrowser);

  })
})

describe('TrackList.vue', () => {
  it('renders correctly', () => {
    const items = [{ title: 'foo', upnpclass: 'object.item.audioItem.musicTrack' },
    { title: 'bar', albumArtURI: '/bar.png', upnpclass: 'object.item.audioItem.musicTrack' }]
    let wrapper = mount(TrackList, { propsData: { items, heading: 'My heading' }, stubs: { RouterLink: RouterLinkStub } });
    expect(wrapper.element).toMatchSnapshot();
  })
})

describe('CoverImageGrid.vue', () => {
  it('renders correctly', () => {
    const items = [{ title: 'foo', upnpclass: 'object.item.audioItem.musicTrack' },
    { title: 'bar', albumArtURI: '/bar.png', upnpclass: 'object.item.audioItem.musicTrack' }]
    let wrapper = mount(CoverImageGrid, { propsData: { items, heading: 'My heading' }, stubs: { RouterLink: RouterLinkStub } });
    expect(wrapper.element).toMatchSnapshot();
  })
})

describe('ContainerBrowserMixin', () => {
  const Component = { template: '<div></div>', mixins: [ContainerBrowserMixin] };
  const children = [
    { name: 'foo', upnpclass: 'object.container.album.musicAlbum' },
    { name: 'item2', upnpclass: 'object.item.audioItem' },
    { name: 'item42', upnpclass: 'object.container.album.fooBar' },
    { name: 'noname', upnpclass: 'object.item.audioItem.musicTrack' }]
  let wrapper;

  beforeEach(async () => {
    ControlPoint.browseServer.mockResolvedValueOnce(children)
    wrapper = mount(Component, { propsData: { item: { id: '1234' }, udn: '456' } });
    await wrapper.vm.$nextTick();
  })

  it('retrieves the childitems of the container', () => {
    expect(wrapper.vm.children).toEqual(children);
    expect(wrapper.vm.musicAlbums).toEqual([children[0]]);
  })
  it('filters musicAlbum subcontainers', () => {
    expect(wrapper.vm.musicAlbums).toEqual([children[0]]);
  })
  it('filters musicTrack subitems', () => {
    expect(wrapper.vm.musicTracks).toEqual([children[3]]);
  })
})
