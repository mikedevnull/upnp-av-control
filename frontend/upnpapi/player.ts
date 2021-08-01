import { NuxtAxiosInstance } from '@nuxtjs/axios'
import { PlaybackInfo, PlayerDevice } from './types'
import { adaptTo } from './utils'

export function getDevices(connector: NuxtAxiosInstance) {
  // return testData.renderer
  const url = '/api/player/'
  return connector
    .get(url)
    .then((response: any) => response.data as PlayerDevice[])
}

export function play(
  connector: NuxtAxiosInstance,
  player: PlayerDevice,
  itemid: string
) {
  const url = `/api/player/${player.id}/queue`
  connector.post(url, { library_item_id: itemid })
}

export function playbackInfo(connector: NuxtAxiosInstance, playerId: string) {
  const url = `/api/player/${playerId}/playback`
  return connector
    .get(url)
    .then((response: any) => response.data)
    .then((data: any) => adaptTo<PlaybackInfo>(data))
}
