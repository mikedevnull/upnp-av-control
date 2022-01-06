import { TopBar, PlayerListItem } from "../components";
import { ReactComponent as NavBackIcon } from "../assets/nav-back.svg";
import { useHistory } from "react-router-dom";
import { PlayerDevice } from "../upnpapi/types";

interface PlayerSelectionProps {
  devices: PlayerDevice[];
  selectedPlayerId?: string;
  selectionHandler?: CallableFunction;
}

export default function PlayerSelection(props: PlayerSelectionProps) {
  const history = useHistory();
  const nav = (
    <button>
      <NavBackIcon onClick={() => history.goBack()} />
    </button>
  );

  const entries = props.devices.map((player) => (
    <PlayerListItem
      clickHandler={props.selectionHandler}
      key={player.id}
      player={player}
      selected={player.id === props.selectedPlayerId}
    />
  ));

  return (
    <>
      <TopBar nav={nav} /> <div>{entries}</div>
    </>
  );
}
