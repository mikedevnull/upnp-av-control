import React from "react";
import { cleanup, waitFor, render, act } from "@testing-library/react";
import BackendConnectionStateView from "./backend-connection-state-view";
import { PlaybackControl } from "../upnpapi";

jest.mock("../upnpapi/playback_control");

afterEach(cleanup);

describe("BackendConnectionStateView", () => {
  it("show error view when backend connection is lost", async () => {
    const playbackControl = new PlaybackControl();

    const { queryByText } = render(
      <BackendConnectionStateView playbackControl={playbackControl} />
    );

    const element = queryByText(/ERROR/i);
    expect(element).toHaveClass("hidden");

    act(() => {
      playbackControl.fakeBackendState.mockReturnValue("disconnected");
      playbackControl.emit("backend-state-changed");
    });

    await waitFor(() => expect(element).not.toHaveClass("hidden"));
  });

  it("hides error view when backend connection is connected", async () => {
    const playbackControl = new PlaybackControl();
    playbackControl.fakeBackendState.mockReturnValue('disconnected')

    const { queryByText } = render(
      <BackendConnectionStateView playbackControl={playbackControl} />
    );

    const element = queryByText(/ERROR/i);
    expect(element).not.toHaveClass("hidden");

    act(() => {
      playbackControl.fakeBackendState.mockReturnValue('connected')
      playbackControl.emit("backend-state-changed");
    });

    await waitFor(() => expect(element).toHaveClass("hidden"));
  });
});
