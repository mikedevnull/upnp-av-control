import { useEffect, useReducer } from "react";
import { PlaybackControl } from "./upnpapi";
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
      type: "active-player-presence";
      isPresent: boolean;
    }
  | {
      type: "playback-info-changed";
      playbackInfo: PlaybackInfo;
    };

function reducer(
  pc: PlaybackControl,
  state: PlayerControlState,
  action: Action
) {
  switch (action.type) {
    case "active-player-presence":
      let playerName = "";
      if (action.isPresent) {
        playerName = pc.selectedPlayerName;
      }
      return { ...state, playerPresent: action.isPresent, playerName };
    case "playback-info-changed":
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
      type: "active-player-presence",
      isPresent,
    });
  const playbackInfoDispatch = (playbackInfo: PlaybackInfo) =>
    dispatch({
      type: "playback-info-changed",
      playbackInfo,
    });
  useEffect(() => {
    presenceDispatch(playbackControl.isPlayerPresent);
    playbackInfoDispatch(playbackControl.playbackInfo);
    playbackControl.on("active-player-presence", presenceDispatch);
    playbackControl.on("playback-info-changed", playbackInfoDispatch);
    return () => {
      playbackControl.off("active-player-presence", presenceDispatch);
      playbackControl.off("playback-info-changed", playbackInfoDispatch);
    };
  }, [playbackControl]);
  return state;
}
