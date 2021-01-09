import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import ControlPointEventBus from "@/controlpoint-event-bus.js";

const localVue = createLocalVue();

localVue.use(Vuex);

describe("UpnpEventBus", () => {
  let store;
  let actions;
  let createMockWebsocket;
  let socketMock;
  beforeEach(() => {
    actions = {
      updateAvailableRenderers: jest.fn(),
      updateAvailableServers: jest.fn()
    };
    store = new Vuex.Store({ actions });
    socketMock = {
      url: undefined,
      onmessage: undefined,
      close: jest.fn(),
      send: jest.fn()
    };
    createMockWebsocket = jest.fn(url => {
      socketMock.url = url;
      return socketMock;
    });
  });

  it("should create a websocket", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(createMockWebsocket).toHaveBeenCalled();
  });

  it("should set its state to connected on initial handsake", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe("closed");
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}'
    });
    expect(bus.state).toBe("connected");
  });

  it("should request discovery notifications", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}'
    });
    expect(socketMock.send).toHaveBeenCalled();
    const requestdata = JSON.parse(socketMock.send.mock.calls[0][0]);
    expect(requestdata.jsonrpc).toBe("2.0");
    expect(requestdata.method).toBe("subscribe");
    expect(requestdata.params.category).toBe("discovery");
  });

  it("should reject wrong versions on initial handsake", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe("closed");
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.1.0" }}'
    });
    expect(bus.state).toBe("closed");
    expect(socketMock.close).toHaveBeenCalled();
  });

  it("should handle wrong payload data on initial handsake", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(bus.state).toBe("closed");
    socketMock.onmessage({ data: '{ "foo": "bar" }' });
    expect(bus.state).toBe("closed");
    expect(socketMock.close).toHaveBeenCalled();
  });

  it("should trigger initial data updates on startup", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    expect(actions.updateAvailableRenderers).toHaveBeenCalled();
    expect(actions.updateAvailableServers).toHaveBeenCalled();
  });

  it("should trigger a data update on new device events", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    // handshake
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}'
    });
    // actual event
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "new_device", "params":{"udn": "1234", "device_type": "MediaRenderer" }}'
    });
    // once on run(), once on event
    expect(actions.updateAvailableRenderers).toHaveBeenCalledTimes(2);
  });

  it("should trigger a data update on new device losts", () => {
    const bus = new ControlPointEventBus(store, createMockWebsocket);
    bus.run();
    // handshake
    socketMock.onmessage({
      data:
        '{ "jsonrpc": "2.0", "method": "device_lost", "params":{"udn": "1234", "device_type": "MediaRenderer" }}'
    }); // actual event
    // once on run(), once on event
    expect(actions.updateAvailableRenderers).toHaveBeenCalledTimes(2);
  });
});
