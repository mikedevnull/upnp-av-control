import { EventBus, ControlPointState, PlaybackInfoMessage } from "./event_bus";
import { PlaybackInfo, PlayerDevice } from "./types";
import { api } from ".";
import EventEmitter from "eventemitter3";
import _ from "lodash";

export type PlaybackControlEvent =
  | "playback-devices-changed"
  | "active-player-presence"
  | "playback-info-changed"
  | "backend-state-changed";

export type PlaybackControlState = "connected" | "disconnected";
export default class PlaybackControl extends EventEmitter<PlaybackControlEvent> {
  private _selectedPlayerId?: string;
  private _playerPresent: boolean = false;
  private _players: ArrayLike<PlayerDevice> = [];
  private _playbackInfo: PlaybackInfo = {
    volumePercent: 0,
    transport: "STOPPED",
    album: null,
    title: null,
    artist: null,
  };

  constructor(private readonly _eventBus: EventBus) {
    super();
    const storedId = localStorage.getItem("selected-player-id");
    if (storedId) {
      this._selectedPlayerId = storedId;
    }
    this._eventBus.on("new-device", this.updateDevices.bind(this));
    this._eventBus.on("device-lost", this.updateDevices.bind(this));
    this._eventBus.on(
      "playback-info-update",
      (message: PlaybackInfoMessage) => {
        this._playbackInfo = message.playbackinfo;
        this.emit("playback-info-changed", this._playbackInfo);
      }
    );
    this._eventBus.on(
      "connection-state-changed",
      this.onBusStateChanged.bind(this)
    );
    this.onBusStateChanged(this._eventBus.state);
  }

  async playItemsImmediatly(itemIds: string[]) {
    if (!this.isPlayerPresent || this._selectedPlayerId === undefined) {
      return;
    }
    await api.stop(this._selectedPlayerId);
    await api.setPlaybackQueue(this._selectedPlayerId, itemIds);
    this._playbackInfo.transport = "PLAYING";
    this._playbackInfo.title = "";
    this._playbackInfo.artist = "";
    this._playbackInfo.album = "";
    this.emit("playback-info-changed", this._playbackInfo);
    await api.play(this._selectedPlayerId);
  }

  async playPause() {
    if (!this.isPlayerPresent || this._selectedPlayerId === undefined) {
      return;
    }
    if (this._playbackInfo.transport === "PLAYING") {
      this._playbackInfo.transport = "STOPPED";
      this.emit("playback-info-changed", this._playbackInfo);
      api.stop(this._selectedPlayerId);
    } else if (this._playbackInfo.transport === "STOPPED") {
      this._playbackInfo.transport = "PLAYING";
      this.emit("playback-info-changed", this._playbackInfo);
      api.play(this._selectedPlayerId);
    }
  }

  setVolume(volume: number) {
    if (!this.isPlayerPresent || this._selectedPlayerId === undefined) {
      return;
    }
    if (this._playbackInfo.volumePercent != volume) {
      this._playbackInfo.volumePercent = volume;
      this.emit("playback-info-changed", this._playbackInfo);
      api.setVolume(this._selectedPlayerId, volume);
    }
  }

  get backendState(): PlaybackControlState {
    return this._eventBus.state !== "connected" ? "disconnected" : "connected";
  }

  get playbackInfo() {
    return this._playbackInfo;
  }

  get availablePlayers() {
    return this._players;
  }

  get isPlayerPresent() {
    return this._playerPresent;
  }

  get selectedPlayerId(): string | undefined {
    return this._selectedPlayerId;
  }

  set selectedPlayerId(playerId: string | undefined) {
    if (this._selectedPlayerId === playerId) {
      return;
    }
    if (this.isPlayerPresent && this._selectedPlayerId) {
      this._eventBus.unsubscribePlaybackInfo(this._selectedPlayerId);
    }
    this._selectedPlayerId = playerId;
    if (playerId) {
      localStorage.setItem("selected-player-id", playerId);
    } else {
      localStorage.removeItem("selected-player-id");
    }
    this.checkSelectedPlayerPresence();
  }

  get selectedPlayerName() {
    if (this.isPlayerPresent) {
      const selectedPlayer = _.find(
        this._players,
        (p) => p.id === this._selectedPlayerId
      );
      if (selectedPlayer) {
        return selectedPlayer.name;
      }
    }
    return "";
  }

  private async updateDevices() {
    const devices = await api.getDevices();
    if (_.isEqual(devices, this._players) === false) {
      this._players = devices;
      this.emit("playback-devices-changed", devices);
      this.checkSelectedPlayerPresence();
    }
  }

  private checkSelectedPlayerPresence() {
    let changed = false;
    if (this._selectedPlayerId === undefined) {
      if (this._playerPresent === true) {
        this._playerPresent = false;
        changed = true;
      }
    } else {
      const selectedPlayer = _.find(
        this._players,
        (p) => p.id === this._selectedPlayerId
      );
      const newState = selectedPlayer !== undefined;
      if (newState !== this._playerPresent) {
        this._playerPresent = newState;
        changed = true;
      }
    }
    if (changed) {
      this.emit("active-player-presence", this._playerPresent);
    }
    if (this._playerPresent && this._selectedPlayerId) {
      this._eventBus.subscribePlaybackInfo(this._selectedPlayerId);
      api.getPlaybackInfo(this._selectedPlayerId).then((data) => {
        this._playbackInfo = data;
        this.emit("playback-info-changed", this._playbackInfo);
      });
    }
  }

  private onBusStateChanged(state: ControlPointState) {
    if (state === "connected") {
      this.updateDevices();
    }
    this.emit("backend-state-changed");
  }
}
