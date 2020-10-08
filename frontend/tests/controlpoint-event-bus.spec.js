import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import ControlPointEventBus from '@/controlpoint-event-bus.js'


const localVue = createLocalVue()

localVue.use(Vuex)

describe('UpnpEventBus', () => {
  let store;
  let actions;
  let createMockWebsocket;
  let socketMock;
  beforeEach(() => {
    actions = {
      update_available_renderers: jest.fn(),
      update_available_servers: jest.fn(),
      update_playback_info: jest.fn()
    }
    store = new Vuex.Store({ actions })
    socketMock = { url: undefined, onmessage: undefined, close: jest.fn() }
    createMockWebsocket = jest.fn(url => { socketMock.url = url; return socketMock; })
  });

  it('should create a websocket', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(createMockWebsocket).toHaveBeenCalled();
  })

  it('should set its state to connected on initial handsake', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe('closed')
    socketMock.onmessage({ data: '{ "version": "0.0.1" }' })
    expect(bus.state).toBe('connected')
  })

  it('should reject wrong versions on initial handsake', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe('closed')
    socketMock.onmessage({ data: '{ "version": "0.0.2" }' })
    expect(bus.state).toBe('closed')
    expect(socketMock.close).toHaveBeenCalled()
  })

  it('should wrong payload data on initial handsake', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe('closed')
    socketMock.onmessage({ data: '{ "foo": "bar" }' })
    expect(bus.state).toBe('closed')
    expect(socketMock.close).toHaveBeenCalled()
  })

  it('should trigger initial data updates on startup', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(actions.update_available_renderers).toHaveBeenCalled()
    expect(actions.update_available_servers).toHaveBeenCalled()
    expect(actions.update_playback_info).toHaveBeenCalled()
  })

  it('should trigger a data update on new device events', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    // handshake
    socketMock.onmessage({ data: '{ "version": "0.0.1" }' })
    // actual event
    socketMock.onmessage({ data: '{"event_type": "NEW_DEVICE"}' })
    // once on run(), once on event
    expect(actions.update_available_renderers).toHaveBeenCalledTimes(2);
    expect(actions.update_available_servers).toHaveBeenCalledTimes(2)
    expect(actions.update_playback_info).toHaveBeenCalledTimes(2)
  })

  it('should trigger a data update on new device losts', () => {
    let bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    // handshake
    socketMock.onmessage({ data: '{ "version": "0.0.1" }' })
    // actual event
    socketMock.onmessage({ data: '{"event_type": "DEVICE_LOST"}' })
    // once on run(), once on event
    expect(actions.update_available_renderers).toHaveBeenCalledTimes(2);
    expect(actions.update_available_servers).toHaveBeenCalledTimes(2)
    expect(actions.update_playback_info).toHaveBeenCalledTimes(2)
  })
})
