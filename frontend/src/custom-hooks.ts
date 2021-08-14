import { useEffect, useReducer } from "react";
import { PlaybackControl } from "./upnpapi";

interface PlayerControlState {
  playerPresent: boolean;
  playerName: string;
}

const initialState = {
  playerPresent: false,
  playerName: "",
};

type Action = {
  type: typeof PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED;
  isPresent: boolean;
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
  useEffect(() => {
    dispatch({
      type: PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
      isPresent: playbackControl.isPlayerPresent,
    });
    playbackControl.on(
      PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
      presenceDispatch
    );
    return () => {
      playbackControl.off(
        PlaybackControl.Event.ACTIVE_PLAYER_PRESENCE_CHANGED,
        presenceDispatch
      );
    };
  }, [playbackControl]);
  return state;
}
