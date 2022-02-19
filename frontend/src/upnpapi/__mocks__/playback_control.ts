import EventEmitter from "eventemitter3";
import { PlaybackControlState } from "../playback_control";

export default class MockPlaybackControl extends EventEmitter {
  playItemsImmediatly = jest.fn();
  fakeBackendState = jest.fn().mockReturnValue("connected");
  get backendState(): PlaybackControlState {
    return this.fakeBackendState();
  }
}
