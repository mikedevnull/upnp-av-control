import JsonRPCClient from "./jsonrpc";
import { PlaybackInfo } from "./types";
import { adaptTo } from "./utils";

function websocketUrl(socketPath: string) {
  const loc = window.location;
  return (
    (loc.protocol === "https:" ? "wss://" : "ws://") +
    loc.host +
    loc.pathname +
    socketPath
  );
}

interface WebSocketFactory {
  (url: string): WebSocket;
}

type InitMessage = {
  version: string;
};

type NewDeviceMessage = {
  udn: string;
  deviceType: string;
};

type DeviceLostMessage = {
  udn: string;
  deviceType: string;
};

export type PlaybackInfoMessage = {
  id: string;
  playbackinfo: PlaybackInfo;
};

interface OnDeviceLostCallback {
  (message: DeviceLostMessage): void;
}

interface OnNewDeviceCallback {
  (message: NewDeviceMessage): void;
}

interface OnErrorCallback {
  (message: string): void;
}
interface PlaybackInfoCallback {
  (message: PlaybackInfoMessage): void;
}

function createWebsocket(url: string) {
  return new WebSocket(url);
}

type ControlPointState = "closed" | "connected";
export default class ControlPointEventBus {
  socketUrl: string;
  socketFactory: WebSocketFactory;
  socket: WebSocket;
  jrpc: JsonRPCClient;
  state: ControlPointState;
  onerror: OnErrorCallback | undefined;
  onNewDevice: OnNewDeviceCallback | undefined;
  onDeviceLost: OnDeviceLostCallback | undefined;
  onPlaybackInfo: PlaybackInfoCallback | undefined;

  constructor(socketFactory: WebSocketFactory = createWebsocket) {
    this.socketUrl = websocketUrl("api/ws/events");
    this.socketFactory = socketFactory;
    this.socket = this.socketFactory(this.socketUrl);
    this.jrpc = new JsonRPCClient();
    this.state = "closed";
    this.onerror = undefined;

    this.jrpc.onerror = (message: string) => {
      if (this.state === "connected") {
        this.socket.close();
      }
      if (this.onerror) {
        this.onerror("JSONRPC Error: " + message);
      }
    };
    this.jrpc.on("initialize", (params: InitMessage) =>
      this._onInitialize(params.version)
    );
    this.jrpc.on("new_device", (params: any) => {
      if (this.onNewDevice) {
        this.onNewDevice(adaptTo<NewDeviceMessage>(params));
      }
    });
    this.jrpc.on("device_lost", (params: any) => {
      if (this.onDeviceLost) {
        this.onDeviceLost(adaptTo<DeviceLostMessage>(params));
      }
    });
    this.jrpc.on("playbackinfo", (params: any) => {
      console.log(params);
      if (this.onPlaybackInfo) {
        this.onPlaybackInfo(adaptTo<PlaybackInfoMessage>(params.playbackinfo));
      }
    });

    this.socket.onmessage = (event) => {
      console.log(event.data);
      this.jrpc.handleMessage(event.data);
    };
    this.socket.onclose = () => {};
    this.jrpc.streamTo = (_msg: string) => {
      this.socket.send(_msg);
    };
  }

  _onInitialize(version: string) {
    if (this.state === "connected") {
      return;
    }
    if (version !== "0.2.0") {
      this.socket.close();
      return;
    }
    this.state = "connected";
    console.log("event-bus connected");
    this.jrpc.call("subscribe", { category: "discovery" });
  }

  async subscribePlaybackInfo(playerid: string) {
    const data = {
      category: "playbackinfo",
      udn: playerid,
    };
    await this.jrpc.call("subscribe", data);
  }

  async unsubscribePlaybackInfo(playerid: string) {
    const data = {
      category: "playbackinfo",
      udn: playerid,
    };
    await this.jrpc.call("unsubscribe", data);
  }
}
