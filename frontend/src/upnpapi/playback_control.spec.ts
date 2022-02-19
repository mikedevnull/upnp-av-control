import { api } from ".";
import PlaybackControl from "./playback_control";
import EventBus from "./event_bus";
import { MapLike } from "typescript";

jest.mock("./event_bus");
jest.mock("./api");

const MockEventBus = <jest.Mock<EventBus>>EventBus;
const mockedGetDevice = api.getDevices as jest.Mock;
const mockedPlaybackInfo = api.getPlaybackInfo as jest.Mock;
class LocalStorageMock {
  private store: MapLike<string>;
  constructor() {
    this.store = {};
  }
  clear() {
    this.store = {};
  }

  getItem(key: string) {
    return this.store[key] || null;
  }

  setItem(key: string, value: string) {
    this.store[key] = value;
  }

  removeItem(key: string) {
    delete this.store[key];
  }

  get length() {
    return this.store.keys.length;
  }

  key(n: number) {
    return this.store.keys[n];
  }
}

global.localStorage = new LocalStorageMock();

const devices = [
  { id: "1234", name: "foo" },
  { id: "5678", name: "bar" },
];
const flushPromises = () => new Promise(process.nextTick);

describe("PlaybackControl", () => {
  let eventBus: any;

  beforeAll(() => {});

  beforeEach(() => {
    eventBus = new MockEventBus();
    mockedGetDevice.mockClear();
    mockedPlaybackInfo.mockClear();
    mockedPlaybackInfo.mockResolvedValue({
      id: "1234",
      playbackinfo: { volumePercent: 20 },
    });
    localStorage.clear();
  });

  describe("playback device discovery", () => {
    it("provides a list of available devices", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);

      const control = new PlaybackControl(eventBus);
      await flushPromises();

      expect(api.getDevices).toHaveBeenCalled();
      expect(control.availablePlayers.length).toEqual(2);
    });

    it("emits an event when a new playback devices becomes available", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      const control = new PlaybackControl(eventBus);
      await flushPromises();

      const deviceCb = jest.fn();
      control.on("playback-devices-changed", deviceCb);
      mockedGetDevice.mockReturnValueOnce([{ id: "abc", name: "Baz" }]);

      eventBus.triggerNewDevice({ udn: "abc", deviceType: "renderer" });
      await flushPromises();
      expect(deviceCb).toHaveBeenCalledTimes(1);
    });

    it("emits an event when a playback devices gets lost", async () => {
      mockedGetDevice.mockReturnValue([{ id: "abc", name: "Baz" }]);
      const control = new PlaybackControl(eventBus);
      await flushPromises();

      const deviceCb = jest.fn();
      control.on("playback-devices-changed", deviceCb);
      mockedGetDevice.mockReturnValueOnce([]);

      eventBus.triggerDeviceLost({ udn: "abc", deviceType: "renderer" });
      await flushPromises();
      expect(deviceCb).toHaveBeenCalledTimes(1);
    });
  });

  describe("active player handling", () => {
    it("emits an event when selecting an available playback device", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      await flushPromises();

      control.selectedPlayerId = "1234";
      control.selectedPlayerId = "1234"; // setting it twice should not have any effect

      expect(playerCb).toHaveBeenCalledTimes(1);
      expect(playerCb).toHaveBeenCalledWith(true);
      expect(control.isPlayerPresent).toBeTruthy();
    });

    it("emits an event when a pre-selected playback device becomes available", async () => {
      mockedGetDevice.mockReturnValueOnce([]);
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      await flushPromises();
      control.selectedPlayerId = "1234";
      expect(playerCb).not.toHaveBeenCalled();

      mockedGetDevice.mockReturnValueOnce(devices);
      eventBus.triggerNewDevice({ udn: "1234", deviceType: "renderer" });
      await flushPromises();

      expect(playerCb).toHaveBeenCalledTimes(1);
      expect(playerCb).toHaveBeenCalledWith(true);
      expect(control.isPlayerPresent).toBeTruthy();
    });

    it("emits an event when the selected playback device gets lost", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      control.selectedPlayerId = "1234";
      await flushPromises();
      expect(control.isPlayerPresent).toBeTruthy();

      mockedGetDevice.mockReturnValueOnce([]);
      eventBus.triggerDeviceLost({ udn: "1234", deviceType: "renderer" });
      await flushPromises();

      expect(playerCb).toHaveBeenCalledTimes(2);
      expect(playerCb).toHaveBeenCalledWith(false);
      expect(control.isPlayerPresent).toBeFalsy();
    });

    it("emits an event when active player is set to undefined", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      control.selectedPlayerId = "1234";
      await flushPromises();
      expect(control.isPlayerPresent).toBeTruthy();

      control.selectedPlayerId = undefined;
      expect(playerCb).toHaveBeenCalledTimes(2);
      expect(playerCb).toHaveBeenCalledWith(false);
      expect(control.isPlayerPresent).toBeFalsy();
    });
  });

  describe("selected player persistence", () => {
    it("uses the localstorage to initialize the active player id", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      localStorage.setItem("selected-player-id", "1234");
      const control = new PlaybackControl(eventBus);

      await flushPromises();
      expect(control.selectedPlayerId).toEqual("1234");
      expect(control.isPlayerPresent).toBeTruthy();
    });

    it("stores the selected player id in localstorage", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      const control = new PlaybackControl(eventBus);

      await flushPromises();
      control.selectedPlayerId = "abcd";
      expect(localStorage.getItem("selected-player-id")).toEqual("abcd");
    });
  });

  describe("backend connection state", () => {
    it("emits state change event backend becomes is lost", async () => {
      const control = new PlaybackControl(eventBus);
      expect(control.backendState).toBe("connected");
      const stateCb = jest.fn();
      control.on("backend-state-changed", stateCb);

      await flushPromises();

      eventBus.triggerClosed();
      expect(eventBus.state).toBe("closed");
      expect(control.backendState).toBe("disconnected");
      expect(stateCb).toBeCalledTimes(1);
    });
  });
});
