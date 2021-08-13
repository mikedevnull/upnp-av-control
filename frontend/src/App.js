import "./App.css";
import { LibraryBrowser } from "./pages";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { Player, PlayerSelection } from "./pages";
import { useEffect } from "react";

function App() {
  useEffect(() => {
    console.log("setup upnpapi");
  });

  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/player">
            <Player />
          </Route>
          <Route path="/select-player">
            <PlayerSelection />
          </Route>
          <Route path="/">
            <LibraryBrowser />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
