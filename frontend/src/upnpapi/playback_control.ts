import ControlPointEventBus, { PlaybackInfoMessage } from "./event_bus";
import { PlaybackInfo, PlayerDevice } from "./types";
import * as api from "./player";
import EventEmitter from "eventemitter3";
import _ from "lodash";

enum PlaybackControlEvent {
  DEVICES_CHANGED = "playback-devices-changed",
  ACTIVE_PLAYER_PRESENCE_CHANGED = "active-player-presence",
  PLAYBACK_INFO_CHANGED = "playback-info-changed",
}
export default class PlaybackControl extends EventEmitter {
  public static readonly Event = PlaybackControlEvent;
  readonly Event = PlaybackControl.Event;
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

  constructor(private readonly _eventBus: ControlPointEventBus) {
    super();
    const storedId = localStorage.getItem("selected-player-id");
    if (storedId) {
      this._selectedPlayerId = storedId;
    }
    this._eventBus.onNewDevice = this.updateDevices.bind(this);
    this._eventBus.onDeviceLost = this.updateDevices.bind(this);
    this._eventBus.onPlaybackInfo = (message: PlaybackInfoMessage) => {
      this._playbackInfo = message.playbackinfo;
      this.emit(PlaybackControlEvent.PLAYBACK_INFO_CHANGED, this._playbackInfo);
    };
    this.updateDevices();
  }

  play(itemId: string) {
    if (this._selectedPlayerId) {
      api.play(this._selectedPlayerId, itemId);
    }
  }

  setVolume(volume: number) {
    if (this._selectedPlayerId) {
      api.setVolume(this._selectedPlayerId, volume);
    }
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
      this.emit(PlaybackControl.Event.DEVICES_CHANGED, devices);
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
      this.emit(
        PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
        this._playerPresent
      );
    }
    if (this._playerPresent && this._selectedPlayerId) {
      this._eventBus.subscribePlaybackInfo(this._selectedPlayerId);
      api.playbackInfo(this._selectedPlayerId).then((data) => {
        this._playbackInfo = data;
      });
    }
  }
}
