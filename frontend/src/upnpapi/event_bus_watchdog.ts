import { ControlPointState, EventBus } from "./event_bus";

export class EventBusWatchdog {
  private reconnectInterval?: number;
  private readonly RECONNECTION_INTERVAL_MS = 2500;

  constructor(private readonly _eventBus: EventBus) {
    this._eventBus.on(
      "connection-state-changed",
      (state: ControlPointState) => {
        if (state === "closed") {
          this._onDisconnect();
        }
      }
    );

    if (this._eventBus.state == "closed") {
      this._onDisconnect();
    }
  }

  private _onDisconnect() {
    if (!this.reconnectInterval) {
      this.reconnectInterval = window.setInterval(() => {
        this._reconnect();
      }, this.RECONNECTION_INTERVAL_MS);
    }
  }

  private _reconnect() {
    if (this._eventBus.state !== "closed") {
      window.clearInterval(this.reconnectInterval);
      this.reconnectInterval = undefined;
    } else {
      console.log("Backend connection closed - reconnecting");
      this._eventBus.connect();
    }
  }
}
