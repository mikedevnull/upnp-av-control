import _ from "lodash";
import EventEmitter from "eventemitter3";
import {
  NewDeviceMessage,
  DeviceLostMessage,
  PlaybackInfoMessage,
  ControlPointState,
  ControlPointEvents,
} from "../event_bus";

export default class MockEventBus extends EventEmitter<ControlPointEvents> {
  private _state: ControlPointState = "closed";

  private infoSubscriptions = new Array<String>();

  triggerDeviceLost(data: DeviceLostMessage) {
    this.emit("device-lost", data);
  }
  triggerNewDevice(data: NewDeviceMessage) {
    this.emit("new-device", data);
  }
  triggerClosed() {
    if (this._state !== "closed") {
      this._state = "closed";
      this.emit("connection-state-changed", "closed");
    }
  }
  get state() {
    return this._state;
  }

  subscribePlaybackInfo(playerId: string) {
    this.infoSubscriptions.push(playerId);
  }
  unsubscribePlaybackInfo(playerId: string) {
    _.remove(this.infoSubscriptions, (x) => x === playerId);
  }
}
