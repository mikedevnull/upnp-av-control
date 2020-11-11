import { mutations, getters, actions } from "@/store";
jest.mock("@/upnpapi");
import upnpapi from "@/upnpapi";

describe("mutations", () => {
  it('should set the volume with "setVolume"', () => {
    const state = { volume: 0 };
    mutations.setVolume(state, 42);
    expect(state.volume).toBe(42);
  });

  it('should set available renderers with "setAvailableRenderers"', () => {
    const state = { availableRenderers: ["foo", "faa"] };
    mutations.setAvailableRenderers(state, ["foo", "bar"]);
    expect(state.availableRenderers).toEqual(["foo", "bar"]);
  });

  it('should set available renderers with "setAvailableServers"', () => {
    const state = { availableServers: ["foo", "faa"] };
    mutations.setAvailableServers(state, ["foo", "bar"]);
    expect(state.availableServers).toEqual(["foo", "bar"]);
  });

  it('should set available renderers with "setActivePlayer"', () => {
    const state = { activePlayer: "foo" };
    mutations.setActivePlayer(state, "foo");
    expect(state.activePlayer).toBe("foo");
  });
});

describe("getters", () => {
  it("should return a media server given by its UDN", () => {
    const state = {
      availableServers: [{ udn: "foo" }, { udn: "bar" }, { udn: "1234" }]
    };
    const server1 = getters.getMediaServerByUDN(state)("foo");
    expect(server1.udn).toBe("foo");
    const server2 = getters.getMediaServerByUDN(state)("987");
    expect(server2).toBeUndefined();
  });
});

describe("actions", () => {
  it("should commit renderers queried from the backend API", async () => {
    const fakedRenderers = [
      { name: "foo", udn: "123" },
      { name: "bar", udn: "345" }
    ];
    upnpapi.getMediaRenderers.mockReturnValueOnce(fakedRenderers);
    const context = { commit: jest.fn() };
    await actions.updateAvailableRenderers(context);
    expect(context.commit).toHaveBeenCalledWith(
      "setAvailableRenderers",
      fakedRenderers
    );
  });

  it("should commit servers queried from the backend API", async () => {
    const fakedServers = [
      { name: "foo", udn: "123" },
      { name: "bar", udn: "345" }
    ];
    upnpapi.getLibraryDevices.mockReturnValueOnce(fakedServers);
    const context = { commit: jest.fn() };
    await actions.updateAvailableServers(context);
    expect(context.commit).toHaveBeenCalledWith(
      "setAvailableServers",
      fakedServers
    );
  });

  it("should commit playback info queried from the backend API", async () => {
    const playbackInfo = { volume: 42, player: "foo" };
    upnpapi.getCurrentPlaybackInfo.mockReturnValueOnce(playbackInfo);
    const context = { commit: jest.fn() };
    await actions.updatePlaybackInfo(context);
    expect(context.commit).toHaveBeenCalledWith("setActivePlayer", "foo");
    expect(context.commit).toHaveBeenCalledWith("setVolume", 42);
  });
});
