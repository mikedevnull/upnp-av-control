import _ from "lodash";
import EventEmitter from "eventemitter3";
import {
  NewDeviceMessage,
  DeviceLostMessage,
  EventBus,
  ControlPointState,
  ControlPointEvents,
  PlaybackInfoMessage,
} from "../event_bus";

export default class MockedEventBus
  extends EventEmitter<ControlPointEvents>
  implements EventBus
{
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
      this.triggerStateChange("closed");
    }
  }
  triggerStateChange(targetState: ControlPointState) {
    this._state = targetState;
    this.emit("connection-state-changed", targetState);
  }
  triggerPlaybackInfoChange(info: PlaybackInfoMessage) {
    this.emit("playback-info-update", info);
  }

  get state() {
    return this._state;
  }

  async subscribePlaybackInfo(playerId: string) {
    this.infoSubscriptions.push(playerId);
  }
  async unsubscribePlaybackInfo(playerId: string) {
    _.remove(this.infoSubscriptions, (x) => x === playerId);
  }
}
