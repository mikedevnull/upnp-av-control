import _ from "lodash";

export default class MockEventBus {
  onNewDevice: { (message: any): void } | undefined;
  onDeviceLost: { (message: any): void } | undefined;
  private infoSubscriptions = new Array<String>();

  triggerDeviceLost(data: { udn: string; deviceType: string }) {
    if (this.onDeviceLost) {
      this.onDeviceLost(data);
    }
  }
  triggerNewDevice(data: { udn: string; deviceType: string }) {
    if (this.onNewDevice) {
      this.onNewDevice(data);
    }
  }
  subscribePlaybackInfo(playerId: string) {
    this.infoSubscriptions.push(playerId);
  }
  unsubscribePlaybackInfo(playerId: string) {
    _.remove(this.infoSubscriptions, (x) => x === playerId);
  }
}
