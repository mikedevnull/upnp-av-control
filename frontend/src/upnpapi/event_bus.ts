import { EventEmitter } from "eventemitter3";
import JsonRPCClient from "./jsonrpc";
import { PlaybackInfo } from "./types";
import { adaptTo } from "./utils";

function websocketUrl(socketPath: string) {
  const loc = window.location;
  return (
    (loc.protocol === "https:" ? "wss://" : "ws://") + loc.host + socketPath
  );
}

export type NewDeviceMessage = {
  udn: string;
  deviceType: string;
};

export type DeviceLostMessage = {
  udn: string;
  deviceType: string;
};

export type PlaybackInfoMessage = {
  id: string;
  playbackinfo: PlaybackInfo;
};

export type ControlPointState = "closed" | "connecting" | "connected";

export type ControlPointEvents =
  | "new-device"
  | "device-lost"
  | "playback-info-update"
  | "connection-state-changed";

export interface EventBus {
  on<T extends ControlPointEvents>(
    event: ControlPointEvents,
    fn: (...args: any[]) => void,
    context?: any
  ): this;

  subscribePlaybackInfo(playerid: string): Promise<void>;
  unsubscribePlaybackInfo(playerid: string): Promise<void>;

  readonly state: ControlPointState;
}

export default class ControlPointEventBus
  extends EventEmitter<ControlPointEvents>
  implements EventBus
{
  private socketUrl: string;
  private socket?: WebSocket;
  private jrpc: JsonRPCClient;
  private _state: ControlPointState;

  constructor() {
    super();
    this.socketUrl = websocketUrl("/api/ws/events");
    this.jrpc = new JsonRPCClient();
    this._state = "closed";

    this.jrpc.onerror = (message: string) => {
      this.socket?.close();
    };
    this.jrpc.on("initialize", (params: { version: string }) =>
      this._onInitialize(params.version)
    );
    this.jrpc.on("new_device", (params: any) => {
      this.emit("new-device", adaptTo<NewDeviceMessage>(params));
    });
    this.jrpc.on("device_lost", (params: any) => {
      this.emit("device-lost", adaptTo<DeviceLostMessage>(params));
    });
    this.jrpc.on("playbackinfo", (params: any) => {
      this.emit(
        "playback-info-update",
        adaptTo<PlaybackInfoMessage>({
          id: params.udn,
          playbackinfo: params.playbackinfo,
        })
      );
    });

    this.connect();
  }

  get state() {
    return this._state;
  }

  _onInitialize(version: string) {
    if (this._state === "connected") {
      return;
    }
    if (version !== "0.2.0") {
      this.socket?.close();
      return;
    }
    this._changeStateTo("connected");
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

  connect() {
    if (this._state !== "closed") {
      return;
    }
    this.socket = new WebSocket(this.socketUrl);
    this.socket.onmessage = (event) => {
      this.jrpc.handleMessage(event.data);
    };
    this.socket.onclose = () => {
      this._changeStateTo("closed");
    };
    this.jrpc.streamTo = (_msg: string) => {
      this.socket?.send(_msg);
    };
  }

  _changeStateTo(targetState: ControlPointState) {
    if (this._state === targetState) {
      return;
    }
    this._state = targetState;
    this.emit("connection-state-changed", this._state);
  }
}
