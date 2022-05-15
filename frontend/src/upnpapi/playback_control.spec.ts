import { api } from ".";

import PlaybackControl from "./playback_control";
import MockedEventBus from "./__mocks__/event_bus";

jest.mock("./api");

const mockedGetDevice = api.getDevices as jest.Mock;
const mockedPlaybackInfo = api.getPlaybackInfo as jest.Mock;

const devices = [
  { id: "1234", name: "foo" },
  { id: "5678", name: "bar" },
];
const flushPromises = () => new Promise(process.nextTick);

describe("PlaybackControl", () => {
  let eventBus: MockedEventBus;
  let eventBusOn: jest.SpiedFunction<typeof eventBus.on>;

  beforeAll(() => {});

  beforeEach(() => {
    eventBus = new MockedEventBus();
    eventBusOn = jest.spyOn(eventBus, "on");
    mockedGetDevice.mockClear();
    mockedGetDevice.mockResolvedValue(devices);
    mockedPlaybackInfo.mockClear();
    mockedPlaybackInfo.mockResolvedValue({
      id: "1234",
      playbackinfo: { volumePercent: 20 },
    });
    localStorage.clear();
  });

  describe("playback device discovery", () => {
    it("provides a list of available devices", async () => {
      const control = new PlaybackControl(eventBus);
      eventBus.triggerStateChange("connected");
      await flushPromises();
      expect(api.getDevices).toHaveBeenCalled();
      expect(control.availablePlayers.length).toEqual(2);
    });
    it("emits an event when a new playback devices becomes available", async () => {
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);
      await flushPromises();

      const deviceCb = jest.fn();
      control.on("playback-devices-changed", deviceCb);
      mockedGetDevice.mockResolvedValueOnce([{ id: "abc", name: "Baz" }]);
      eventBus.triggerNewDevice({ udn: "abc", deviceType: "renderer" });
      await flushPromises();

      expect(deviceCb).toHaveBeenCalledTimes(1);
    });
    it("emits an event when a playback devices gets lost", async () => {
      mockedGetDevice.mockResolvedValue([{ id: "abc", name: "Baz" }]);
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);
      await flushPromises();
      const deviceCb = jest.fn();
      control.on("playback-devices-changed", deviceCb);
      mockedGetDevice.mockResolvedValueOnce([]);
      eventBus.triggerDeviceLost({ udn: "abc", deviceType: "renderer" });
      await flushPromises();
      expect(deviceCb).toHaveBeenCalledTimes(1);
    });
  });

  describe("active player handling", () => {
    it("emits an event when selecting an available playback device", async () => {
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      expect(control.selectedPlayerName).toBe("");

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      await flushPromises();

      control.selectedPlayerId = "1234";
      control.selectedPlayerId = "1234"; // setting it twice should not have any effect

      expect(playerCb).toHaveBeenCalledTimes(1);
      expect(playerCb).toHaveBeenCalledWith(true);
      expect(control.isPlayerPresent).toBeTruthy();
      expect(control.selectedPlayerName).toBe("foo");
    });

    it("emits an event when a pre-selected playback device becomes available", async () => {
      mockedGetDevice.mockResolvedValueOnce([]);
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      await flushPromises();
      control.selectedPlayerId = "1234";
      expect(playerCb).not.toHaveBeenCalled();

      mockedGetDevice.mockResolvedValueOnce(devices);
      eventBus.triggerNewDevice({ udn: "1234", deviceType: "renderer" });
      await flushPromises();

      expect(playerCb).toHaveBeenCalledTimes(1);
      expect(playerCb).toHaveBeenCalledWith(true);
      expect(control.isPlayerPresent).toBeTruthy();
      expect(control.selectedPlayerName).toBe("foo");
    });

    it("emits an event when the selected playback device gets lost", async () => {
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      const playerCb = jest.fn();
      control.on("active-player-presence", playerCb);
      control.selectedPlayerId = "1234";
      await flushPromises();
      expect(control.isPlayerPresent).toBeTruthy();

      mockedGetDevice.mockResolvedValueOnce([]);
      eventBus.triggerDeviceLost({ udn: "1234", deviceType: "renderer" });
      await flushPromises();

      expect(playerCb).toHaveBeenCalledTimes(2);
      expect(playerCb).toHaveBeenCalledWith(false);
      expect(control.isPlayerPresent).toBeFalsy();
      expect(control.selectedPlayerName).toBe("");
    });

    it("emits an event when active player is set to undefined", async () => {
      eventBus.triggerStateChange("connected");
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
      expect(control.selectedPlayerName).toBe("");
    });
  });

  describe("selected player persistence", () => {
    it("uses the localstorage to initialize the active player id", async () => {
      localStorage.setItem("selected-player-id", "1234");
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      await flushPromises();
      expect(control.selectedPlayerId).toEqual("1234");
      expect(control.isPlayerPresent).toBeTruthy();
    });

    it("stores the selected player id in localstorage", async () => {
      mockedGetDevice.mockReturnValueOnce(devices);
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      await flushPromises();
      control.selectedPlayerId = "abcd";
      expect(localStorage.getItem("selected-player-id")).toEqual("abcd");
    });
  });

  describe("backend connection state", () => {
    it("initializes itself on backend connection", async () => {
      const control = new PlaybackControl(eventBus);
      expect(control.backendState).toBe("disconnected");

      await flushPromises();

      expect(mockedGetDevice).not.toHaveBeenCalled();
      expect(eventBusOn).toHaveBeenCalledTimes(4);

      eventBus.triggerStateChange("connected");
      expect(control.backendState).toBe("connected");

      await flushPromises();

      expect(mockedGetDevice).toHaveBeenCalledTimes(1);
    });

    it("initializes itself when also when event bus already connected", async () => {
      eventBus.triggerStateChange("connected");

      const control = new PlaybackControl(eventBus);
      expect(control.backendState).toBe("connected");

      expect(mockedGetDevice).toHaveBeenCalledTimes(1);
    });

    it("emits state change event on backend state changes", async () => {
      const control = new PlaybackControl(eventBus);
      expect(control.backendState).toBe("disconnected");

      const stateCb = jest.fn();
      control.on("backend-state-changed", stateCb);

      eventBus.triggerStateChange("connecting");

      expect(control.backendState).toBe("disconnected");

      eventBus.triggerStateChange("connected");
      expect(control.backendState).toBe("connected");

      eventBus.triggerStateChange("closed");
      expect(control.backendState).toBe("disconnected");

      expect(stateCb).toHaveBeenCalledTimes(3);
    });

    it("reinitializes after backend reconnect", async () => {
      eventBus.triggerStateChange("connected");
      const control = new PlaybackControl(eventBus);

      eventBus.triggerStateChange("closed");

      eventBus.triggerStateChange("connected");

      expect(mockedGetDevice).toHaveBeenCalledTimes(2);
    });

    describe("playback info handling", () => {
      beforeEach(() => {
        eventBus.triggerStateChange("connected");
      });
      it("should forward and store playback info changes", async () => {
        const control = new PlaybackControl(eventBus);
        const oldInfo = control.playbackInfo;

        const infoCb = jest.fn();
        control.on("playback-info-changed", infoCb);

        const newInfo = {
          transport: "PLAYING",
          volumePercent: 10,
          title: "t",
          album: "al",
          artist: "ar",
        };
        eventBus.triggerPlaybackInfoChange({
          id: "foo",
          playbackinfo: newInfo,
        });
        await flushPromises();

        expect(infoCb).toHaveBeenCalledTimes(1);
        expect(infoCb).toHaveBeenCalledWith(newInfo);
        expect(control.playbackInfo).toEqual(newInfo);
        expect(control.playbackInfo).not.toEqual(oldInfo);
      });
    });
  });
});
