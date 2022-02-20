import Player from "./player";
import { MemoryRouter } from "react-router-dom";
import { createMemoryHistory } from "history";
import { cleanup, fireEvent, render } from "@testing-library/react";
import PlaybackControl from "../upnpapi/playback_control";
import { isRegExp } from "lodash";

afterEach(cleanup);
jest.mock("../upnpapi/playback_control");

describe("Player", () => {
  let history;
  let control;
  beforeEach(() => {
    history = createMemoryHistory();
    control = new PlaybackControl();
  });

  describe("Buttons and inputs", () => {
    it("toggles play/pause on playback controller",()=>{
    const { queryByLabelText } = render(
      <MemoryRouter>
        <Player playbackControl={control}/>
      </MemoryRouter>
    );
    const playPauseBtn = queryByLabelText('PlayPause')
    expect(playPauseBtn).toBeTruthy()
    fireEvent.click(playPauseBtn);
    expect(control.playPause).toHaveBeenCalledTimes(1);
  })


  it("changes volume in input range change", () => {
    const { queryByLabelText } = render(
      <MemoryRouter>
        <Player playbackControl={control}/>
      </MemoryRouter>
    );
    const volumeSlider = queryByLabelText('Volume')
    expect(volumeSlider).toBeTruthy()
    fireEvent.change(volumeSlider, {target:{value: 3}});
    expect(control.setVolume).toHaveBeenCalledWith(3);
  });
});
});

