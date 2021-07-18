import { NuxtAxiosInstance } from '@nuxtjs/axios'
import ControlPointEventBus from './event_bus'
import * as library from './library'
import * as player from './player'

export default (connector: NuxtAxiosInstance) => {
  const eventBus = new ControlPointEventBus()
  return {
    eventBus,
    getMediaRenderers() {
      return player.getDevices(connector)
    },
    play(device: player.PlayerDevice, itemid: string) {
      return player.play(connector, device, itemid)
    },
    browseLibrary(id: string) {
      return library.browse(connector, id)
    },
    getLibraryItem(id: string) {
      return library.getItem(connector, id)
    },
  }
}
