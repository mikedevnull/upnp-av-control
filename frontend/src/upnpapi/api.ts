import { PlaybackInfo, PlayerDevice } from "./types";
import { LibraryListItem } from "./types";
import { adaptTo } from "./utils";

export function getDevices() {
  // return testData.renderer
  const url = "/api/player/";
  return fetch(url).then(
    (response) => response.json() as Promise<PlayerDevice[]>
  );
}

export function play(playerId: string, itemid: string) {
  const url = `/api/player/${playerId}/queue`;
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ library_item_id: itemid }),
  });
}

export function getPlaybackInfo(playerId: string) {
  const url = `/api/player/${playerId}/playback`;
  return fetch(url)
    .then((response: any) => response.json())
    .then((data: any) => adaptTo<PlaybackInfo>(data));
}

export function setVolume(playerId: string, volume: number) {
  if (volume < 0 || volume > 100) {
    throw new Error("volume out of valid range");
  }
  const url = `/api/player/${playerId}/playback`;
  fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ volume_percent: volume }),
  });
}

export function browse(id?: string) {
  let url = `/api/library/`;
  if (id) {
    url = `/api/library/${id}`;
  }
  return fetch(url)
    .then((response: any) => response.json())
    .then((data: any) => adaptTo<LibraryListItem[]>(data));
}

export function getItem(id: string) {
  const url = `/api/library/${id}/metadata`;
  return fetch(url)
    .then((response: any) => response.json())
    .then((data: any) => adaptTo<LibraryListItem>(data));
}
