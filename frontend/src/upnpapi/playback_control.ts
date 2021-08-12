import ControlPointEventBus from "./event_bus";
import { PlayerDevice } from "./types";
import { getDevices } from "./player";
import EventEmitter from "eventemitter3";
import _ from "lodash";

export enum PlaybackControlEvent {
  DEVICES_CHANGED = "playback-devices-changed",
  ACTIVE_PLAYER_PRESENT = "active-player-present",
  ACTIVE_PLAYER_LOST = "active-player-lost",
}
export default class PlaybackControl extends EventEmitter {
  private _selectedPlayerId?: string;
  private _playerPresent: boolean = false;
  private _players: ArrayLike<PlayerDevice> = [];

  constructor(private readonly _eventBus: ControlPointEventBus) {
    super();

    _eventBus.onNewDevice = this.updateDevices.bind(this);
    _eventBus.onDeviceLost = this.updateDevices.bind(this);
    this.updateDevices();
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
    this._selectedPlayerId = playerId;
    this.checkSelectedPlayerPresence();
  }

  private async updateDevices() {
    const devices = await getDevices();
    if (_.isEqual(devices, this._players) === false) {
      this._players = devices;
      this.emit(PlaybackControlEvent.DEVICES_CHANGED, devices);
      this.checkSelectedPlayerPresence();
    }
  }

  private checkSelectedPlayerPresence() {
    if (this._selectedPlayerId === undefined) {
      if (this._playerPresent === true) {
        this._playerPresent = false;
        this.emit(PlaybackControlEvent.ACTIVE_PLAYER_LOST);
      }
      return;
    }
    const selectedPlayer = _.find(
      this._players,
      (p) => p.id === this._selectedPlayerId
    );
    const newState = selectedPlayer !== undefined;
    if (newState !== this._playerPresent) {
      this._playerPresent = newState;
      if (newState) {
        this.emit(PlaybackControlEvent.ACTIVE_PLAYER_PRESENT);
      } else {
        this.emit(PlaybackControlEvent.ACTIVE_PLAYER_LOST);
      }
    }
  }
}
