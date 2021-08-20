import { useEffect, useReducer } from "react";
import { PlaybackControl } from "./upnpapi";
import { PlaybackInfoMessage } from "./upnpapi/event_bus";
import { PlaybackInfo } from "./upnpapi/types";

interface PlayerControlState {
  playerPresent: boolean;
  playerName: string;
  volumePercent: number;
  title: string | null;
  album: string | null;
  artist: string | null;
  transport: string;
}

const initialState = {
  playerPresent: false,
  playerName: "",
  volumePercent: 0,
  title: null,
  artist: null,
  album: null,
  transport: "STOPPED",
};

type Action =
  | {
      type: typeof PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED;
      isPresent: boolean;
    }
  | {
      type: typeof PlaybackControl.Event.PLAYBACK_INFO_CHANGED;
      playbackInfo: PlaybackInfo;
    };

function reducer(
  pc: PlaybackControl,
  state: PlayerControlState,
  action: Action
) {
  switch (action.type) {
    case PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED:
      let playerName = "";
      if (action.isPresent) {
        playerName = pc.selectedPlayerName;
      }
      return { ...state, playerPresent: action.isPresent, playerName };
    case PlaybackControl.Event.PLAYBACK_INFO_CHANGED:
      return { ...state, ...action.playbackInfo };
    default:
      throw new Error();
  }
}

export function usePlayerControl(playbackControl: PlaybackControl) {
  const [state, dispatch] = useReducer(
    (s: PlayerControlState, a: Action) => reducer(playbackControl, s, a),
    initialState
  );
  const presenceDispatch = (isPresent: boolean) =>
    dispatch({
      type: PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
      isPresent,
    });
  const playbackInfoDispatch = (playbackInfo: PlaybackInfo) =>
    dispatch({
      type: PlaybackControl.Event.PLAYBACK_INFO_CHANGED,
      playbackInfo,
    });
  useEffect(() => {
    presenceDispatch(playbackControl.isPlayerPresent);
    playbackInfoDispatch(playbackControl.playbackInfo);
    playbackControl.on(
      PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
      presenceDispatch
    );
    playbackControl.on(
      PlaybackControl.Event.PLAYBACK_INFO_CHANGED,
      playbackInfoDispatch
    );
    return () => {
      playbackControl.off(
        PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
        presenceDispatch
      );
      playbackControl.off(
        PlaybackControl.Event.PLAYBACK_INFO_CHANGED,
        playbackInfoDispatch
      );
    };
  }, [playbackControl]);
  return state;
}
