import * as api from "./player";
import PlaybackControl from "./playback_control";
import { PlaybackControlEvent } from "./playback_control";
import MockEventBus from "./event_bus";
jest.mock("./event_bus");
jest.mock("./player");

const devices = [
  { id: "1234", name: "foo" },
  { id: "5678", name: "bar" },
];
const flushPromises = () => new Promise(setImmediate);

describe("PlaybackControl", () => {
  let eventBus;

  beforeAll(() => {});

  beforeEach(() => {
    eventBus = new MockEventBus();
    jest.clearAllMocks();
  });

  it("provides a list of available devices", async () => {
    api.getDevices.mockReturnValueOnce(devices);

    const control = new PlaybackControl(eventBus);
    await flushPromises();

    expect(api.getDevices).toHaveBeenCalled();
    expect(control.availablePlayers.length).toEqual(2);
  });

  it("emits an event when a new playback devices becomes available", async () => {
    api.getDevices.mockReturnValue([]);
    const control = new PlaybackControl(eventBus);

    const deviceCb = jest.fn();
    control.on(PlaybackControlEvent.DEVICES_CHANGED, deviceCb);
    api.getDevices.mockReturnValueOnce([{ id: "abc", name: "Baz" }]);

    eventBus.triggerNewDevice({ udn: "abc", deviceType: "renderer" });
    await flushPromises();
    expect(deviceCb).toHaveBeenCalledTimes(1);
  });

  it("emits an event when a playback devices gets lost", async () => {
    api.getDevices.mockReturnValue([{ id: "abc", name: "Baz" }]);
    const control = new PlaybackControl(eventBus);
    await flushPromises();

    const deviceCb = jest.fn();
    control.on(PlaybackControlEvent.DEVICES_CHANGED, deviceCb);
    api.getDevices.mockReturnValueOnce([]);

    eventBus.triggerDeviceLost({ udn: "abc", deviceType: "renderer" });
    await flushPromises();
    expect(deviceCb).toHaveBeenCalledTimes(1);
  });

  it("emits an event when selecting an available playback device", async () => {
    api.getDevices.mockReturnValueOnce(devices);
    const control = new PlaybackControl(eventBus);

    const playerCb = jest.fn();
    control.on(PlaybackControlEvent.ACTIVE_PLAYER_PRESENT, playerCb);
    await flushPromises();

    control.selectedPlayerId = "1234";
    control.selectedPlayerId = "1234"; // setting it twice should not have any effect

    expect(playerCb).toHaveBeenCalledTimes(1);
    expect(control.isPlayerPresent).toBeTruthy();
  });

  it("emits an event when a pre-selected playback device becomes available", async () => {
    api.getDevices.mockReturnValueOnce([]);
    const control = new PlaybackControl(eventBus);

    const playerCb = jest.fn();
    control.on(PlaybackControlEvent.ACTIVE_PLAYER_PRESENT, playerCb);
    await flushPromises();
    control.selectedPlayerId = "1234";
    expect(playerCb).not.toHaveBeenCalled();

    api.getDevices.mockReturnValueOnce(devices);
    eventBus.triggerNewDevice({ udn: "1234", deviceType: "renderer" });
    await flushPromises();

    expect(playerCb).toHaveBeenCalledTimes(1);
    expect(control.isPlayerPresent).toBeTruthy();
  });

  it("emits an event when the selected playback device gets lost", async () => {
    api.getDevices.mockReturnValueOnce(devices);
    const control = new PlaybackControl(eventBus);

    const playerCb = jest.fn();
    control.on(PlaybackControlEvent.ACTIVE_PLAYER_LOST, playerCb);
    control.selectedPlayerId = "1234";
    await flushPromises();
    expect(control.isPlayerPresent).toBeTruthy();

    eventBus.triggerDeviceLost({ udn: "1234", deviceType: "renderer" });
    api.getDevices.mockReturnValueOnce([]);
    await flushPromises();

    expect(playerCb).toHaveBeenCalledTimes(1);
    expect(control.isPlayerPresent).toBeFalsy();
  });

  it("emits an event when active player is set to undefined", async () => {
    api.getDevices.mockReturnValueOnce(devices);
    const control = new PlaybackControl(eventBus);

    const playerCb = jest.fn();
    control.on(PlaybackControlEvent.ACTIVE_PLAYER_LOST, playerCb);
    control.selectedPlayerId = "1234";
    await flushPromises();
    expect(control.isPlayerPresent).toBeTruthy();

    control.selectedPlayerId = undefined;
    expect(playerCb).toHaveBeenCalledTimes(1);
    expect(control.isPlayerPresent).toBeFalsy();
  });
});
