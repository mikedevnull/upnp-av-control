import JsonRPCClient from "./jsonrpc";
import { PlaybackInfo } from "./types";
import { adaptTo } from "./utils";

function websocketUrl(socketPath: string) {
  const loc = window.location;
  return (
    (loc.protocol === "https:" ? "wss://" : "ws://") + loc.host + socketPath
  );
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

type ControlPointState = "closed" | "connecting" | "connected";
export default class ControlPointEventBus {
  socketUrl: string;
  socket: WebSocket;
  jrpc: JsonRPCClient;
  state: ControlPointState;
  onClosed?: () => void;
  onNewDevice?: (message: NewDeviceMessage) => void;
  onDeviceLost?: (message: DeviceLostMessage) => void;
  onPlaybackInfo?: (message: PlaybackInfoMessage) => void;

  constructor() {
    this.socketUrl = websocketUrl("/api/ws/events");
    this.socket = new WebSocket(this.socketUrl);
    this.jrpc = new JsonRPCClient();
    this.state = "connecting";
    this.onClosed = undefined;

    this.jrpc.onerror = (message: string) => {
      this.socket.close();
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
      if (this.onPlaybackInfo) {
        this.onPlaybackInfo(
          adaptTo<PlaybackInfoMessage>({
            id: params.udn,
            playbackinfo: params.playbackinfo,
          })
        );
      }
    });

    this.socket.onmessage = (event) => {
      this.jrpc.handleMessage(event.data);
    };
    this.socket.onclose = () => {
      console.log("websocket connection closed");
      this.state = "closed";
      if (this.onClosed) {
        this.onClosed();
      }
    };
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
