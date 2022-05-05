import "./App.css";
import { LibraryBrowser } from "./pages";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Player, PlayerSelection, PlayerQueue } from "./pages";
import { useEffect, useState, useRef } from "react";
import { ControlPointEventBus, PlaybackControl } from "./upnpapi";
import { BackendConnectionStateView} from './components';
import { EventBusWatchdog } from "./upnpapi/event_bus_watchdog";


const eventBus = new ControlPointEventBus()
const playbackControlInstance = new PlaybackControl(eventBus);
const eventBusWatchDog = new EventBusWatchdog(eventBus)

function App() {
  const playbackControl = useRef(playbackControlInstance);
  const [devices, setDevices] = useState([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState(
    playbackControl.current.selectedPlayerId
  );
  
  useEffect(() => {
    setDevices(playbackControl.current.availablePlayers);
    playbackControl.current.on(
      "playback-devices-changed",
      setDevices
    );
  }, []);
  function selectPlayer(playerId) {
    setSelectedPlayerId(playerId);
    playbackControl.current.selectedPlayerId = playerId;
  }

  return (
    <BrowserRouter>
      <div className="App">
        <BackendConnectionStateView playbackControl={playbackControl.current}/>
        <Routes>
          <Route
            path="/player"
            element={<Player playbackControl={playbackControl.current} />}
          ></Route>
          <Route
            path="/select-player"
            element={
              <PlayerSelection
                devices={devices}
                selectedPlayerId={selectedPlayerId}
                selectionHandler={selectPlayer}
              />
            }
          ></Route>
          <Route
            path="/player-queue"
            element={<PlayerQueue selectedPlayerId={selectedPlayerId} />}
          ></Route>
          <Route
            path="/"
            element={
              <LibraryBrowser playbackControl={playbackControl.current} />
            }
          ></Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
