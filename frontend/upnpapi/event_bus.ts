import JsonRPCClient from './jsonrpc'

function websocketUrl(socketPath: string) {
  const loc = window.location
  return (
    (loc.protocol === 'https:' ? 'wss://' : 'ws://') +
    loc.host +
    loc.pathname +
    socketPath
  )
}

interface WebSocketFactory {
  (url: string): WebSocket
}

function createWebsocket(url: string) {
  return new WebSocket(url)
}

export default class ControlPointEventBus {
  socketUrl: string
  socketFactory: WebSocketFactory
  socket: WebSocket
  jrpc: JsonRPCClient | null
  constructor(socketFactory: WebSocketFactory = createWebsocket) {
    //     this.store = undefined
    this.socketUrl = websocketUrl('api/ws/events')
    this.socketFactory = socketFactory
    this.socket = this.socketFactory(this.socketUrl)
    //     this.state = 'closed'
    this.jrpc = null
    //     this.onerror = undefined
  }

  init() {}
  //   updateStoreData() {
  //     this.store.dispatch('updateAvailableRenderers')
  //     this.store.dispatch('updateAvailableServers')
  //   }
  //   onInitialize(version) {
  //     if (this.state === 'connected') {
  //       return
  //     }
  //     if (version !== '0.2.0') {
  //       this.socket.close()
  //       return
  //     }
  //     this.state = 'connected'
  //     console.log('event-bus connected')
  //     this.jrpc.call('subscribe', { category: 'discovery' })
  //   }
  //   onNewDevice(_udn, deviceType) {
  //     if (deviceType === 'MediaRenderer') {
  //       this.store.dispatch('updateAvailableRenderers')
  //     } else if (deviceType === 'MediaServer') {
  //       this.store.dispatch('updateAvailableServers')
  //     }
  //   }
  //   onDeviceLost(_udn, deviceType) {
  //     if (deviceType === 'MediaRenderer') {
  //       this.store.dispatch('updateAvailableRenderers')
  //     } else if (deviceType === 'MediaServer') {
  //       this.store.dispatch('updateAvailableServers')
  //     }
  //   }
}
// const eventBus = new ControlPointEventBus()

// export default function createWebsocketPlugin({ store }) {
//   eventBus.init(store)
// }
