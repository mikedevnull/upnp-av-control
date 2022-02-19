import ControlPointEventBus from "./event_bus";
import WS from "jest-websocket-mock";
import { executionAsyncId } from "async_hooks";

describe("UpnpEventBus", () => {
  let server: WS;
  let bus: ControlPointEventBus;
  beforeEach(async () => {
    server = new WS("ws://localhost/api/ws/events", { jsonProtocol: true });
    bus = new ControlPointEventBus();
    await server.connected;
  });
  afterEach(() => {
    WS.clean();
  });

  describe("connection handling", () => {
    it("should set its state to connected on initial handsake", async () => {
      expect(bus.state).toBe("closed");

      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      expect(bus.state).toBe("connected");
    });

    it("should ignore additional handshake message if already connected", async () => {
      expect(bus.state).toBe("closed");

      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      expect(bus.state).toBe("connected");

      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      expect(bus.state).toBe("connected");
    });

    it("should reject wrong versions on initial handsake", async () => {
      expect(bus.state).toBe("closed");
      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.1.0" },
      });
      await server.closed;
      expect(bus.state).toBe("closed");
    });

    it("should handle wrong payload data on initial handsake", async () => {
      const bus = new ControlPointEventBus();
      await server.connected;
      expect(bus.state).toBe("closed");

      server.send({ foo: "bar" });

      await server.closed;
      expect(bus.state).toBe("closed");
    });
  });

  describe("event processing", () => {
    beforeEach(async () => {
      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
    });

    it("should request discovery notifications", async () => {
      await expect(server).toReceiveMessage({
        id: 1,
        jsonrpc: "2.0",
        method: "subscribe",
        params: { category: "discovery" },
      });
    });

    it("should handle wrong payload data by closing the connection", async () => {
      bus.onerror = jest.fn();
      server.send({ foo: "bar" });
      await server.closed;
      expect(bus.onerror).toHaveBeenCalledTimes(1);
      expect(bus.state).toBe("closed");
    });

    it("should trigger a data update on new device events", async () => {
      bus.onNewDevice = jest.fn();

      server.send({
        jsonrpc: "2.0",
        method: "new_device",
        params: { udn: "1234", device_type: "MediaRenderer" },
      });
      expect(bus.onNewDevice).toHaveBeenCalledTimes(1);
    });

    it("should trigger a data update on device loss", async () => {
      bus.onDeviceLost = jest.fn();
      // actual event
      server.send({
        jsonrpc: "2.0",
        method: "device_lost",
        params: { udn: "1234", device_type: "MediaRenderer" },
      });

      expect(bus.onDeviceLost).toHaveBeenCalledTimes(1);
    });

    it("should subscribe to playback info events", async () => {
      await expect(server).toReceiveMessage({
        id: 1,
        jsonrpc: "2.0",
        method: "subscribe",
        params: { category: "discovery" },
      });

      const subscribePromise = bus.subscribePlaybackInfo("1234");

      await expect(server).toReceiveMessage({
        id: 2,
        jsonrpc: "2.0",
        method: "subscribe",
        params: { udn: "1234", category: "playbackinfo" },
      });
      server.send({ id: 2, jsonrpc: "2.0", result: true });

      await subscribePromise;
    });

    it("should unsubscribe from playback info events", async () => {
      await expect(server).toReceiveMessage({
        id: 1,
        jsonrpc: "2.0",
        method: "subscribe",
        params: { category: "discovery" },
      });

      const unsubscribePromise = bus.unsubscribePlaybackInfo("1234");

      await expect(server).toReceiveMessage({
        id: 2,
        jsonrpc: "2.0",
        method: "unsubscribe",
        params: { udn: "1234", category: "playbackinfo" },
      });

      server.send({ id: 2, jsonrpc: "2.0", result: true });

      await unsubscribePromise;
    });

    it("should trigger a playbackinfo update on update", () => {
      bus.onPlaybackInfo = jest.fn();
      server.send({
        jsonrpc: "2.0",
        method: "playbackinfo",
        params: { udn: "1234", playbackinfo: { volume_percent: 20 } },
      });

      expect(bus.onPlaybackInfo).toHaveBeenCalledTimes(1);
      expect(bus.onPlaybackInfo).toHaveBeenLastCalledWith({
        id: "1234",
        playbackinfo: { volumePercent: 20 },
      });
    });
  });
});
