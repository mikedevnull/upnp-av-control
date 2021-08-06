import "./App.css";
import { LibraryBrowser } from "./pages";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import { Player } from "./pages";

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/player">
            <Player />
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
