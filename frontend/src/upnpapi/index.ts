import * as library from "./library";
import * as player from "./player";
import * as types from "./types";
export { default as ControlPointEventBus } from "./event_bus";
export { default as PlaybackControl } from "./playback_control";

export default class UpnpApi {
  // public readonly eventBus = new ControlPointEventBus();
  getMediaRenderers() {
    return player.getDevices();
  }
  play(device: types.PlayerDevice, itemid: string) {
    return player.play(device, itemid);
  }
  getPlaybackInfo(id: string) {
    return player.playbackInfo(id);
  }
  browseLibrary(id: string) {
    return library.browse(id);
  }
  getLibraryItem(id: string) {
    return library.getItem(id);
  }
}
