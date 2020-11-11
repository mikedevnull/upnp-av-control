function websocketUrl(socketPath) {
  const loc = window.location;
  return (
    (loc.protocol === "https:" ? "wss://" : "ws://") +
    loc.host +
    loc.pathname +
    socketPath
  );
}

function createWebsocket(url) {
  return new WebSocket(url);
}

class ControlPointEventBus {
  constructor(store, socketFactory = createWebsocket) {
    this.store = store;
    this.socketUrl = websocketUrl("api/ws/events");
    this.socketFactory = socketFactory;
    this.socket = null;
    this.state = "closed";
  }

  run() {
    this.updateStoreData();
    this.socket = this.socketFactory(this.socketUrl);
    this.socket.onmessage = event => {
      this.handleMessage(event);
    };
  }

  handleMessage(event) {
    const payload = JSON.parse(event.data);
    if (this.state == "closed") {
      // handshake
      if (payload.version != "0.0.1") {
        console.log("Version mismatch: " + payload.version);
        this.socket.close();
        return;
      }
      this.state = "connected";
      return;
    }
    if (
      payload.event_type == "NEW_DEVICE" ||
      payload.event_type == "DEVICE_LOST"
    ) {
      console.log("devices changed, should update state");
      this.updateStoreData();
    }
  }

  updateStoreData() {
    this.store.dispatch("updateAvailableRenderers");
    this.store.dispatch("updateAvailableServers");
    this.store.dispatch("updatePlaybackInfo");
  }
}

export default ControlPointEventBus;
