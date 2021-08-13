import ControlPointEventBus from "./event_bus";

describe("UpnpEventBus", () => {
  let createMockWebsocket;
  let socketMock;
  beforeEach(() => {
    socketMock = {
      url: undefined,
      onmessage: undefined,
      close: jest.fn(),
      send: jest.fn(),
    };
    createMockWebsocket = jest.fn((url) => {
      socketMock.url = url;
      return socketMock;
    });
  });

  it("should create a websocket", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    expect(createMockWebsocket).toHaveBeenCalled();
  });

  it("should set its state to connected on initial handsake", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    expect(bus.state).toBe("closed");
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    expect(bus.state).toBe("connected");
  });

  it("should request discovery notifications", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    expect(socketMock.send).toHaveBeenCalled();
    const requestdata = JSON.parse(socketMock.send.mock.calls[0][0]);
    expect(requestdata.jsonrpc).toBe("2.0");
    expect(requestdata.method).toBe("subscribe");
    expect(requestdata.params.category).toBe("discovery");
  });

  it("should reject wrong versions on initial handsake", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);

    expect(bus.state).toBe("closed");
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.1.0" }}',
    });
    expect(bus.state).toBe("closed");
    expect(socketMock.close).toHaveBeenCalled();
  });

  it("should handle wrong payload data on initial handsake", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    expect(bus.state).toBe("closed");
    socketMock.onmessage({ data: '{ "foo": "bar" }' });
    expect(bus.state).toBe("closed");
  });

  it("should handle wrong payload data by closing the cpnnection", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    bus.onerror = jest.fn();
    expect(bus.state).toBe("closed");
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    expect(bus.state).toBe("connected");
    socketMock.onmessage({ data: '{ "foo": "bar" }' });
    expect(bus.onerror).toHaveBeenCalledTimes(1);
    expect(bus.state).toBe("closed");
  });

  it("should trigger a data update on new device events", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    const deviceCb = jest.fn();
    bus.onNewDevice = deviceCb;
    // handshake
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    // actual event
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "new_device", "params":{"udn": "1234", "device_type": "MediaRenderer" }}',
    });
    expect(deviceCb).toHaveBeenCalledTimes(1);
  });

  it("should trigger a data update on device loss", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    const deviceCb = jest.fn();
    bus.onDeviceLost = deviceCb;
    // handshake
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "device_lost", "params":{"udn": "1234", "device_type": "MediaRenderer" }}',
    }); // actual event

    expect(deviceCb).toHaveBeenCalledTimes(1);
  });

  it("should subscribe to playback info events", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);

    // handshake
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    socketMock.send.mockClear();
    bus.subscribePlaybackInfo("1234");

    expect(socketMock.send).toHaveBeenCalledTimes(1);
    const data = JSON.parse(socketMock.send.mock.calls[0][0]);
    expect(data).toMatchObject({
      method: "subscribe",
      params: { udn: "1234", category: "playbackinfo" },
    });
  });

  it("should unsubscribe from playback info events", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);

    // handshake
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    socketMock.send.mockClear();
    bus.unsubscribePlaybackInfo("1234");

    expect(socketMock.send).toHaveBeenCalledTimes(1);
    const data = JSON.parse(socketMock.send.mock.calls[0][0]);
    expect(data).toMatchObject({
      method: "unsubscribe",
      params: { udn: "1234", category: "playbackinfo" },
    });
  });

  it("should trigger a playbackinfo update on update", () => {
    const bus = new ControlPointEventBus(createMockWebsocket);
    bus.onPlaybackInfo = jest.fn();
    // handshake
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "initialize", "params":{"version": "0.2.0" }}',
    });
    socketMock.onmessage({
      data: '{ "jsonrpc": "2.0", "method": "playbackinfo", "params":{"udn": "1234", "playbackinfo": {"volume_percent": 20} }}',
    }); // actual event

    expect(bus.onPlaybackInfo).toHaveBeenCalledTimes(1);
    expect(bus.onPlaybackInfo).toHaveBeenLastCalledWith({ volumePercent: 20 });
  });
});
