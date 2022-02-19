import * as api from "./api";
import { enableFetchMocks } from "jest-fetch-mock";
import fetchMock from "jest-fetch-mock";
import { json } from "stream/consumers";
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

  describe("playback queue", () => {
    it("posts items to enqueue for playback", async () => {
      await api.setPlaybackQueue("somePlayerId", ["item1", "item2"]);
      expect(fetchMock).toHaveBeenCalledWith("/api/player/somePlayerId/queue", {
        method: "PUT",
        body: JSON.stringify({ items: [{ id: "item1" }, { id: "item2" }] }),
        headers: { "Content-Type": "application/json" },
      });
    });

    it("post empty item list to clear queue", async () => {
      await api.clearQueue("somePlayerId");
      expect(fetchMock).toHaveBeenCalledWith("/api/player/somePlayerId/queue", {
        method: "PUT",
        body: JSON.stringify({ items: [] }),
        headers: { "Content-Type": "application/json" },
      });
    });

    it("retrieves list of items in playback queue", async () => {
      const item1 = {
        id: "item1",
        title: "title 1",
        artist: "artist 1",
        album: "album 1",
        image: "image url 1",
      };
      const item2 = {
        id: "item2",
        title: "title 2",
      };
      fetchMock.mockResponse(
        JSON.stringify({
          current_item_index: 1,
          items: [item1, item2],
        })
      );
      const queue = await api.getPlaybackQueue("somePlayerId");
      expect(queue.currentItemIndex).toBe(1);
      expect(queue.items.length).toBe(2);
      expect(queue.items).toContainEqual(item1);
      expect(queue.items).toContainEqual(item2);
    });
  });

  describe("playback state control", () => {
    it("patches transport on play", async () => {
      await api.play("somePlayerId");
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/player/somePlayerId/playback",
        {
          method: "PATCH",
          body: JSON.stringify({ transport: "PLAYING" }),
          headers: { "Content-Type": "application/json" },
        }
      );
    });

    it("patches transport on stop", async () => {
      await api.stop("somePlayerId");
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/player/somePlayerId/playback",
        {
          method: "PATCH",
          body: JSON.stringify({ transport: "STOPPED" }),
          headers: { "Content-Type": "application/json" },
        }
      );
    });
  });

  describe("volume control", () => {
    it("changes volume to value in percent", async () => {
      await api.setVolume("somePlayerId", 22);
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/player/somePlayerId/playback",
        {
          method: "PATCH",
          body: JSON.stringify({ volume_percent: 22 }),
          headers: { "Content-Type": "application/json" },
        }
      );

      expect(() => api.setVolume("id", -1)).toThrow(Error);
      expect(() => api.setVolume("id", 101)).toThrow(Error);
    });
  });
});
