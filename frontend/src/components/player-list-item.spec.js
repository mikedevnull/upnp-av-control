import React from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import PlayerListItem from "./player-list-item";


afterEach(cleanup);

describe("PlayerListItem", () => {
  it("shows a clickable player device entry", () => {
    const player = { name: "Foobar", id: "1234" };
    const selectCallback = jest.fn();
    const { queryByText, getByText } = render(
      <PlayerListItem player={player} clickHandler={selectCallback} />
    );

    expect(queryByText(/Foobar/i)).toBeTruthy();
    const item = getByText(/Foobar/i);
    fireEvent.click(item);

    expect(selectCallback).toHaveBeenCalledTimes(1);
    expect(selectCallback).toHaveBeenCalledWith("1234");
  });

  it("highlights selected player devices", () => {
    const player = { name: "Foobar", id: "1234" };

    const { getByText, rerender } = render(
      <PlayerListItem player={player} selected={false} />
    );
    const item = getByText(/Foobar/i);
    expect(item).not.toHaveClass("bg-primary-lightest");

    rerender(<PlayerListItem player={player} selected={true} />);

    expect(item).toHaveClass("bg-primary-lightest");
  });
});
