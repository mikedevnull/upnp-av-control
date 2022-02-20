import EventEmitter from "eventemitter3";
import { PlaybackControlState } from "../playback_control";

export default class MockPlaybackControl extends EventEmitter {
  playItemsImmediatly = jest.fn();
  playPause = jest.fn();
  setVolume = jest.fn();

  fakeBackendState = jest.fn().mockReturnValue("connected");
  fakePlayerPresent = jest.fn().mockReturnValue(true);

  get backendState(): PlaybackControlState {
    return this.fakeBackendState();
  }

  get isPlayerPresent() {
    return this.fakePlayerPresent();
  }
}
