import { PlaybackInfo, PlayerDevice } from "./types";
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

export function playbackInfo(playerId: string) {
  const url = `/api/player/${playerId}/playback`;
  return fetch(url)
    .then((response: any) => response.json())
    .then((data: any) => adaptTo<PlaybackInfo>(data));
}
