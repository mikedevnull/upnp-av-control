import { NuxtAxiosInstance } from '@nuxtjs/axios'
import ControlPointEventBus from './event_bus'

export interface DeviceDescriptor {
  udn: string
  name: string
  icon?: string
}

// function createFakeRenderer(): DeviceDescriptor {
//   return {
//     udn: faker.datatype.uuid(),
//     name: faker.commerce.productName(),
//     icon: faker.image.technics(128, 128),
//   }
// }

// const testData = {
//   renderer: Array.from({ length: 3 }, createFakeRenderer),
// }

function convertDeviceEntry(deviceEntryFromApi: any) {
  return {
    udn: deviceEntryFromApi.udn,
    name: deviceEntryFromApi.name,
  }
}

export default (connector: NuxtAxiosInstance) => {
  const eventBus = new ControlPointEventBus()
  return {
    eventBus,
    getMediaRenderers() {
      // return testData.renderer
      const url = '/player/devices'
      return connector
        .get(url)
        .then((response: any) => response.data.data)
        .then((devices: any) => devices.map(convertDeviceEntry))
    },
    getLibraryDevices() {
      const url = '/library/devices'
      return connector
        .get(url)
        .then((response: any) => response.data)
        .then((devices: any) => devices.map(convertDeviceEntry))
    },
  }
}
