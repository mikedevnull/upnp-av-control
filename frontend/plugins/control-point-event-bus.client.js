// import JsonRPCClient from '~/utils/jsonrpc'

// function websocketUrl(socketPath) {
//   const loc = window.location
//   return (
//     (loc.protocol === 'https:' ? 'wss://' : 'ws://') +
//     loc.host +
//     loc.pathname +
//     socketPath
//   )
// }

// function createWebsocket(url) {
//   return new WebSocket(url)
// }

// class ControlPointEventBus {
//   constructor(socketFactory = createWebsocket) {
//     this.store = undefined
//     this.socketUrl = websocketUrl('api/ws/events')
//     this.socketFactory = socketFactory
//     this.socket = null
//     this.state = 'closed'
//     this.jrpc = null
//     this.onerror = undefined
//   }

//   init(store) {
//     this.store = store
//     this.updateStoreData()
//     this.socket = this.socketFactory(this.socketUrl)
//     this.jrpc = new JsonRPCClient()
//     this.jrpc.onerror = (message) => {
//       if (this.state === 'closed') {
//         this.socket.close()
//       }
//       if (this.onerror) {
//         this.onerror('JSONRPC Error: ' + message)
//       }
//     }
//     this.jrpc.on('initialize', (params) => this.onInitialize(params.version))
//     this.jrpc.on('new_device', (params) => {
//       console.log(params)
//       this.onNewDevice(params.udn, params.device_type)
//     })
//     this.jrpc.on('device_lost', (params) =>
//       this.onNewDevice(params.udn, params.device_type)
//     )
//     this.socket.onmessage = (event) => {
//       this.jrpc.handleMessage(event.data)
//     }
//     this.socket.onclose = () => {}

//     this.jrpc.streamTo = (_msg) => {
//       this.socket.send(_msg)
//     }
//   }

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
// }
// const eventBus = new ControlPointEventBus()

// export default function createWebsocketPlugin({ store }) {
//   eventBus.init(store)
// }
