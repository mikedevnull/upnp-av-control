import { EventBusWatchdog } from "./event_bus_watchdog";
import MockedEventBus from "./__mocks__/event_bus";

jest.useFakeTimers();

describe("EventBus Watchdog", () => {
  it("should reconnect and retry on connection loss", () => {
    const bus = new MockedEventBus();
    const connectFunc = jest.spyOn(bus, "connect");
    bus.triggerStateChange("connected");
    const watchdog = new EventBusWatchdog(bus);

    jest.advanceTimersByTime(5000);

    expect(connectFunc).not.toHaveBeenCalled();
    connectFunc.mockImplementationOnce(() => {
      bus.triggerStateChange("connecting");
      bus.triggerStateChange("closed");
    });
    bus.triggerStateChange("closed");

    jest.advanceTimersByTime(5000);
    expect(connectFunc).toHaveBeenCalledTimes(2);
  });

  it("should handle initial disconnection state and delays gracefully", () => {
    const bus = new MockedEventBus();
    const connectFunc = jest.spyOn(bus, "connect");
    const watchdog = new EventBusWatchdog(bus);

    jest.advanceTimersByTime(100);
    bus.triggerStateChange("connecting");

    jest.advanceTimersByTime(5000);
    expect(connectFunc).not.toHaveBeenCalled();
    bus.triggerStateChange("connected");

    jest.advanceTimersByTime(5000);
    expect(connectFunc).not.toHaveBeenCalled();
  });
});
