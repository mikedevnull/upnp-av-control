import React from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import PlayerSelection from "./player-selection";
import { createMemoryHistory } from "history";
import { Router } from "react-router-dom";

afterEach(cleanup);

describe("PlayerSelection", () => {
  let history;
  beforeEach(() => {
    history = createMemoryHistory();
  });

  it("shows list of players with the selected player highlighted", () => {
    const players = [
      { name: "Foobar", id: "1234" },
      { name: "BazAudio", id: "5678" },
    ];
    const selectCallback = jest.fn();
    const { queryByText, getByText } = render(
      <Router history={history}>
        <PlayerSelection
          devices={players}
          selectedPlayerId="5678"
          selectionHandler={selectCallback}
        />
      </Router>
    );

    expect(queryByText("Foobar")).toBeTruthy();

    expect(getByText("Foobar")).not.toHaveClass("bg-primary-lightest");
    expect(queryByText("BazAudio")).toBeTruthy();

    expect(getByText("BazAudio")).toHaveClass("bg-primary-lightest");

    expect(selectCallback).toHaveBeenCalledTimes(0);
  });

  it("triggers selection callback on item click", () => {
    const players = [
      { name: "Foobar", id: "1234" },
      { name: "BazAudio", id: "5678" },
    ];
    const selectCallback = jest.fn();
    const { queryByText, getByText } = render(
      <Router history={history}>
        <PlayerSelection
          devices={players}
          selectedPlayerId="5678"
          selectionHandler={selectCallback}
        />
      </Router>
    );

    expect(queryByText("Foobar")).toBeTruthy();

    fireEvent.click(getByText("Foobar"));
    expect(selectCallback).toHaveBeenCalledTimes(1);
    expect(selectCallback).toHaveBeenCalledWith("1234");
  });
});
