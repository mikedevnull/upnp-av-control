import _ from "lodash";
import {
  NewDeviceMessage,
  DeviceLostMessage,
  PlaybackInfoMessage,
  ControlPointState,
} from "../event_bus";

export default class MockEventBus {
  onNewDevice?: (message: NewDeviceMessage) => void;
  onDeviceLost?: (message: DeviceLostMessage) => void;
  onClosed?: () => void;
  private _state: ControlPointState = "connected";

  private infoSubscriptions = new Array<String>();

  triggerDeviceLost(data: DeviceLostMessage) {
    if (this.onDeviceLost) {
      this.onDeviceLost(data);
    }
  }
  triggerNewDevice(data: NewDeviceMessage) {
    if (this.onNewDevice) {
      this.onNewDevice(data);
    }
  }
  triggerClosed() {
    this._state = "closed";
    if (this.onClosed) {
      this.onClosed();
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
