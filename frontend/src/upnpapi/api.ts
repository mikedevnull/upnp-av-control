import { PlaybackInfo, PlaybackQueue, PlayerDevice } from "./types";
import { LibraryListItem } from "./types";
import { adaptTo } from "./utils";

export function getDevices() {
  // return testData.renderer
  const url = "/api/player/";
  return fetch(url).then(
    (response) => response.json() as Promise<PlayerDevice[]>
  );
}

export async function setPlaybackQueue(playerId: string, itemids: string[]) {
  const queueurl = `/api/player/${playerId}/queue`;
  await fetch(queueurl, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      items: itemids.map((id) => ({ id })),
    }),
  });
}

export async function clearQueue(playerId: string) {
  const queueurl = `/api/player/${playerId}/queue`;
  await fetch(queueurl, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ items: [] }),
  });
}

async function _changeTransportState(
  playerId: string,
  targetState: "STOPPED" | "PLAYING"
) {
  const transporturl = `/api/player/${playerId}/playback`;
  await fetch(transporturl, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ transport: targetState }),
  });
}

export async function play(playerId: string) {
  await _changeTransportState(playerId, "PLAYING");
}

export async function stop(playerId: string) {
  await _changeTransportState(playerId, "STOPPED");
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

export function getPlaybackQueue(playerid: string) {
  const url = `/api/player/${playerid}/queue`;
  return fetch(url)
    .then((response: any) => response.json())
    .then((data: any) => adaptTo<PlaybackQueue>(data));
}
