import ControlPointEventBus from "./event_bus";
import {
  ControlPointState,
  ControlPointEvents,
  DeviceLostMessage,
  NewDeviceMessage,
} from "./event_bus";
import WS from "jest-websocket-mock";

import * as util from "util";

function waitForState(
  bus: ControlPointEventBus,
  state: ControlPointState
): Promise<void> {
  return new Promise((resolve, reject) => {
    const success = (val: ControlPointState) => {
      if (val === state) {
        resolve();
        bus.off("connection-state-changed", success);
      }
    };
    bus.on("connection-state-changed", success);
  });
}

function waitForEvent<T>(
  bus: ControlPointEventBus,
  event: ControlPointEvents
): Promise<T> {
  return new Promise((resolve, reject) => {
    const success = (val: T) => {
      resolve(val);
    };
    bus.once(event, success);
  });
}

describe("UpnpEventBus", () => {
  let server: WS;
  let bus: ControlPointEventBus;
  beforeEach(async () => {
    server = new WS("ws://localhost/api/ws/events", { jsonProtocol: true });
  });
  afterEach(() => {
    WS.clean();
  });

  describe("connection handling", () => {
    it("should set its state to connected on initial handsake", async () => {
      bus = new ControlPointEventBus();
      await server.connected;

      waitForState(bus, "connecting");

      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      expect(bus.state).toBe("connected");
      const closedCb = jest.fn();
    });

    it("should ignore additional handshake message if already connected", async () => {
      bus = new ControlPointEventBus();
      await server.connected;
      waitForState(bus, "connecting");

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
      bus = new ControlPointEventBus();
      await server.connected;

      waitForState(bus, "connecting");
      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.1.0" },
      });
      await server.closed;
      expect(bus.state).toBe("closed");
    });

    it("should handle wrong payload data on initial handsake", async () => {
      bus = new ControlPointEventBus();
      await server.connected;
      expect(bus.state).toBe("closed");
      waitForState(bus, "connected");

      server.send({ foo: "bar" });

      await server.closed;
      expect(bus.state).toBe("closed");
    });

    it("invoke closed callback when connection is lost", async () => {
      bus = new ControlPointEventBus();
      await server.connected;

      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      expect(bus.state).toBe("connected");
      const closedCb = jest.fn();
      bus.on("connection-state-changed", closedCb);
      server.close();
      await server.closed;
      expect(bus.state).toBe("closed");
      expect(closedCb).toBeCalledWith("closed");
    });
  });

  describe("event processing", () => {
    beforeEach(async () => {
      bus = new ControlPointEventBus();
      await server.connected;

      const ready = waitForState(bus, "connected");
      server.send({
        jsonrpc: "2.0",
        method: "initialize",
        params: { version: "0.2.0" },
      });
      await ready;
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
      server.send({ foo: "bar" });
      await server.closed;

      expect(bus.state).toBe("closed");
    });

    it("should trigger a data update on new device events", async () => {
      const result = waitForEvent<NewDeviceMessage>(bus, "new-device");

      server.send({
        jsonrpc: "2.0",
        method: "new_device",
        params: { udn: "1234", device_type: "MediaRenderer" },
      });
      await expect(result).resolves.toStrictEqual({
        deviceType: "MediaRenderer",
        udn: "1234",
      });
    });

    it("should trigger a data update on device loss", async () => {
      const result = waitForEvent<DeviceLostMessage>(bus, "device-lost");
      // actual event
      server.send({
        jsonrpc: "2.0",
        method: "device_lost",
        params: { udn: "1234", device_type: "MediaRenderer" },
      });

      await expect(result).resolves.toStrictEqual({
        deviceType: "MediaRenderer",
        udn: "1234",
      });
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
      const playbackInfoCb = jest.fn();
      bus.on("playback-info-update", playbackInfoCb);
      server.send({
        jsonrpc: "2.0",
        method: "playbackinfo",
        params: { udn: "1234", playbackinfo: { volume_percent: 20 } },
      });

      expect(playbackInfoCb).toHaveBeenCalledTimes(1);
      expect(playbackInfoCb).toHaveBeenLastCalledWith({
        id: "1234",
        playbackinfo: { volumePercent: 20 },
      });
    });
  });
});
