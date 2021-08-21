import * as api from "./api";
import { enableFetchMocks } from "jest-fetch-mock";
import fetchMock from "jest-fetch-mock";
enableFetchMocks();

describe("upnp web api", () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it("gets a list of available players", async () => {
    fetchMock.mockResponse(
      JSON.stringify([
        { name: "foo", id: "1234" },
        { name: "bar", id: "5678" },
      ])
    );
    const players = await api.getDevices();
    expect(players.length).toEqual(2);
    expect(players).toContainEqual({ name: "bar", id: "5678" });
    expect(players).toContainEqual({ name: "foo", id: "1234" });
  });

  it("gets playbackinfo of a playback device", async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        volume_percent: 15,
        transport: "STOPPED",
        title: "some title",
        artist: "some artist",
        album: "some album",
      })
    );
    const info = await api.getPlaybackInfo("someplayerid");
    expect(fetchMock).toHaveBeenCalledWith("/api/player/someplayerid/playback");
    expect(info).toEqual({
      volumePercent: 15,
      transport: "STOPPED",
      title: "some title",
      artist: "some artist",
      album: "some album",
    });
  });

  it("retrieves library items for browsing", async () => {
    fetchMock.mockResponse(
      JSON.stringify([
        { id: "1", title: "one", upnpclass: "container" },
        {
          id: "2",
          title: "two",
          parentID: "0",
          upnpclass: "container",
          image: "someimageurl",
        },
      ])
    );
    const items = await api.browse("anotherid");
    expect(fetchMock).toHaveBeenCalledWith("/api/library/anotherid");
    expect(items.length).toBe(2);
  });

  it("retrieves item metadata", async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        id: "anotherid",
        title: "antoher",
        parentID: "4",
        upnpclass: "container",
        image: "someimageurl",
      })
    );
    const metadata = await api.getItem("anotherid");
    expect(fetchMock).toHaveBeenCalledWith("/api/library/anotherid/metadata");
    expect(metadata).toEqual({
      id: "anotherid",
      title: "antoher",
      parentID: "4",
      upnpclass: "container",
      image: "someimageurl",
    });
  });
});
