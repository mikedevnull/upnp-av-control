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

type InitMessage = {
  version: string
}

type NewDeviceMessage = {
  udn: string
  // eslint-disable-next-line camelcase
  device_type: string
}

type DeviceLostMessage = {
  udn: string
  // eslint-disable-next-line camelcase
  device_type: string
}

interface OnDeviceLostCallback {
  (message: DeviceLostMessage): void
}

interface OnNewDeviceCallback {
  (message: NewDeviceMessage): void
}

function createWebsocket(url: string) {
  return new WebSocket(url)
}

type ControlPointState = 'closed' | 'connected'
export default class ControlPointEventBus {
  socketUrl: string
  socketFactory: WebSocketFactory
  socket: WebSocket
  jrpc: JsonRPCClient
  state: ControlPointState
  onerror: CallableFunction | undefined
  onNewDevice: OnNewDeviceCallback | undefined
  onDeviceLost: OnDeviceLostCallback | undefined

  constructor(socketFactory: WebSocketFactory = createWebsocket) {
    //     this.store = undefined
    this.socketUrl = websocketUrl('api/ws/events')
    this.socketFactory = socketFactory
    this.socket = this.socketFactory(this.socketUrl)
    //     this.state = 'closed'
    this.jrpc = new JsonRPCClient()
    this.state = 'closed'
    this.onerror = undefined

    this.jrpc.onerror = (message: string) => {
      if (this.state === 'connected') {
        this.socket.close()
      }
      if (this.onerror) {
        this.onerror('JSONRPC Error: ' + message)
      }
    }
    this.jrpc.on('initialize', (params: InitMessage) =>
      this._onInitialize(params.version)
    )
    this.jrpc.on('new_device', (params: NewDeviceMessage) => {
      if (this.onNewDevice) {
        this.onNewDevice(params)
      }
    })
    this.jrpc.on('device_lost', (params: DeviceLostMessage) => {
      if (this.onDeviceLost) {
        this.onDeviceLost(params)
      }
    })

    this.socket.onmessage = (event) => {
      console.log(event.data)
      this.jrpc.handleMessage(event.data)
    }
    this.socket.onclose = () => {}
    this.jrpc.streamTo = (_msg: string) => {
      this.socket.send(_msg)
    }
  }

  _onInitialize(version: string) {
    if (this.state === 'connected') {
      return
    }
    if (version !== '0.2.0') {
      this.socket.close()
      return
    }
    this.state = 'connected'
    console.log('event-bus connected')
    this.jrpc.call('subscribe', { category: 'discovery' })
  }

  async subscribePlaybackInfo(playerid: string) {
    const data = {
      category: 'playbackinfo',
      udn: playerid,
    }
    await this.jrpc.call('subscribe', data)
  }

  async unsubscribePlaybackInfo(playerid: string) {
    const data = {
      category: 'playbackinfo',
      udn: playerid,
    }
    await this.jrpc.call('unsubscribe', data)
  }
}
