import ControlPointEventBus from "./event_bus";

export type PlayerDevice = {
  id: string;
  name: string;
};

export enum TransportState {
  STOPPED,
  PLAYING,
  PAUSED,
}

export type PlaybackInfo = {
  volumePercent: number;
  title: string;
  artist: string;
  album: string;
  transport: TransportState;
};

export type LibraryListItem = {
  title: string;
  id: string;
  parentID?: string;
  upnpclass: string;
  image?: string;
};

export interface UpnpApi {
  eventBus: ControlPointEventBus;
  getMediaRenderers(): Promise<PlayerDevice[]>;
  play(device: PlayerDevice, itemid: string): void;
  getPlaybackInfo(id: string): Promise<PlaybackInfo>;
  browseLibrary(id: string): Promise<LibraryListItem[]>;
  getLibraryItem(id: string): any;
}
