import { NuxtAxiosInstance } from '@nuxtjs/axios'

export type PlayerDevice = {
  id: string
  name: string
}

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
