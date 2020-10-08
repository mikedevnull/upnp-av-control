import { mutations, getters, actions } from '@/store'
jest.mock('@/upnpapi')
import upnpapi from '@/upnpapi';

describe('mutations', () => {
  it('should set the volume with "set_volume"', () => {
    const state = { volume: 0 }
    mutations.set_volume(state, 42);
    expect(state.volume).toBe(42)
  })

  it('should set available renderers with "set_available_renderers"', () => {
    const state = { available_renderers: ['foo', 'faa'] }
    mutations.set_available_renderers(state, ['foo', 'bar']);
    expect(state.available_renderers).toEqual(['foo', 'bar'])
  })

  it('should set available renderers with "set_available_servers"', () => {
    const state = { available_servers: ['foo', 'faa'] }
    mutations.set_available_servers(state, ['foo', 'bar']);
    expect(state.available_servers).toEqual(['foo', 'bar'])
  })

  it('should set available renderers with "set_active_player"', () => {
    const state = { active_player: 'foo' }
    mutations.set_active_player(state, 'foo');
    expect(state.active_player).toBe('foo')
  })
})

describe('getters', () => {
  it('should return a media server given by its UDN', () => {
    const state = { available_servers: [{ udn: 'foo' }, { udn: 'bar' }, { udn: '1234' }] }
    let server1 = getters.getMediaServerByUDN(state)('foo');
    expect(server1.udn).toBe('foo');
    let server2 = getters.getMediaServerByUDN(state)('987');
    expect(server2).toBeUndefined();
  })
})


describe('actions', () => {
  it('should commit renderers queried from the backend API', async () => {
    let faked_renderers = [{ name: 'foo', udn: '123' }, { name: 'bar', udn: '345' }]
    upnpapi.getMediaRenderers.mockReturnValueOnce(faked_renderers);
    let context = { commit: jest.fn() }
    await actions.update_available_renderers(context);
    expect(context.commit).toHaveBeenCalledWith('set_available_renderers', faked_renderers);
  })

  it('should commit servers queried from the backend API', async () => {
    let faked_servers = [{ name: 'foo', udn: '123' }, { name: 'bar', udn: '345' }]
    upnpapi.getLibraryDevices.mockReturnValueOnce(faked_servers);
    let context = { commit: jest.fn() }
    await actions.update_available_servers(context);
    expect(context.commit).toHaveBeenCalledWith('set_available_servers', faked_servers);
  })

  it('should commit playback info queried from the backend API', async () => {
    let playback_info = { volume: 42, player: 'foo' }
    upnpapi.getCurrentPlaybackInfo.mockReturnValueOnce(playback_info);
    let context = { commit: jest.fn() }
    await actions.update_playback_info(context);
    expect(context.commit).toHaveBeenCalledWith('set_active_player', 'foo');
    expect(context.commit).toHaveBeenCalledWith('set_volume', 42);
  })
})
