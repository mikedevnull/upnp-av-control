import ControlPointEventBus from "./event_bus";
import { PlayerDevice } from "./types";
import { getDevices } from "./player";

export default class PlaybackControl {
  private _selectedPlayerId?: string;
  public readonly playerPresent: boolean = false;
  private _players: ArrayLike<PlayerDevice> = [];

  constructor(private readonly eventBus: ControlPointEventBus) {
    getDevices().then((devices) => (this._players = devices));
  }

  get availablePlayers() {
    return this._players;
  }

  get selectedPlayerId(): string | undefined {
    return this._selectedPlayerId;
  }

  set selectedPlayerId(playerId: string | undefined) {
    if (this._selectedPlayerId === playerId) {
      return;
    }
  }
}
