import "./App.css";
import { LibraryBrowser } from "./pages";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { Player, PlayerSelection } from "./pages";
import { useEffect, useState, useRef } from "react";
import { ControlPointEventBus, PlaybackControl } from "./upnpapi";

function createPlaybackControl() {
  const eventBus = new ControlPointEventBus();
  const playbackControl = new PlaybackControl(eventBus);
  return playbackControl;
}

function App() {
  const playbackControl = useRef(createPlaybackControl());
  const [devices, setDevices] = useState([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState(
    playbackControl.current.selectedPlayerId
  );
  useEffect(() => {
    playbackControl.current.on(
      PlaybackControl.Event.DEVICES_CHANGED,
      setDevices
    );
    playbackControl.current.selectedPlayerId =
      "6e5dbd54-1fcc-d911-1346-f1ba79c317e5";
  }, []);
  function selectPlayer(playerId) {
    setSelectedPlayerId(playerId);
    playbackControl.current.selectedPlayerId = playerId;
  }

  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/player">
            <Player playbackControl={playbackControl.current} />
          </Route>
          <Route path="/select-player">
            <PlayerSelection
              devices={devices}
              selectedPlayerId={selectedPlayerId}
              selectionHandler={selectPlayer}
            />
          </Route>
          <Route path="/">
            <LibraryBrowser playbackControl={playbackControl.current} />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
