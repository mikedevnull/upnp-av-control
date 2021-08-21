import React from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import { BrowseListItem } from "./browse-list-item";
import IconContainer from "../assets/folder.svg";
import IconTrack from "../assets/track.svg";

afterEach(cleanup);

describe("PlayerListItem", () => {
  it("shows a library item entry", () => {
    const libraryitem = { title: "Some item", id: "1234" };
    const selectCallback = jest.fn();
    const { queryByText, getByText } = render(
      <BrowseListItem item={libraryitem} clickHandler={selectCallback} />
    );

    expect(queryByText(/Some item/i)).toBeTruthy();
    const item = getByText(/Some item/i);
    fireEvent.click(item);

    expect(selectCallback).toHaveBeenCalledTimes(1);
    expect(selectCallback).toHaveBeenCalledWith(libraryitem);
    const itemImg = item.querySelector("img");
    expect(itemImg.src).toEqual("http://localhost/" + IconContainer);
  });

  it("shows a special placeholder items for tracks without image", () => {
    const libraryitem = { title: "Some item", id: "1234", upnpclass: "item" };
    const { getByText } = render(<BrowseListItem item={libraryitem} />);

    const item = getByText(/Some item/i);

    const itemImg = item.querySelector("img");
    expect(itemImg.src).toEqual("http://localhost/" + IconTrack);
  });

  it("shows the item image if present", () => {
    const libraryitem = {
      title: "Some item",
      id: "1234",
      image: "somefancyuri",
    };
    const { queryByText, getByText } = render(
      <BrowseListItem item={libraryitem} />
    );

    expect(queryByText(/Some item/i)).toBeTruthy();
    const item = getByText(/Some item/i);

    const itemImg = item.querySelector("img");
    expect(itemImg.src).toEqual("http://localhost/" + libraryitem.image);
  });
});
