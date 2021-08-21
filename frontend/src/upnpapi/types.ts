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
