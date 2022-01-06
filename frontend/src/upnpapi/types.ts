import ControlPointEventBus from "./event_bus";

export type PlayerDevice = {
  id: string;
  name: string;
};

export type PlaybackInfo = {
  volumePercent: number;
  title: string | null;
  artist: string | null;
  album: string | null;
  transport: string;
};

export type LibraryListItem = {
  title: string;
  id: string;
  parentID?: string;
  upnpclass: string;
  image?: string;
};

export type PlaybackQueueItem = {
  id: string;
  title: string;
  artist?: string;
  album?: string;
  image?: string;
};

export type PlaybackQueue = {
  currentItemIndex?: number;
  items: PlaybackQueueItem[];
};
