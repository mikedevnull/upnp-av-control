export default class MockEventBus {
  onNewDevice: { (message: any): void } | undefined;
  onDeviceLost: { (message: any): void } | undefined;

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
}
