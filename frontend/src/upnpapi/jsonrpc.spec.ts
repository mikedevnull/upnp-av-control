import JsonRPCClient from "./jsonrpc";

describe("JsonRPCClient notifications", () => {
  it("invokes registered callback on notification", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage('{"jsonrpc": "2.0", "method":"some_notification"}');
    expect(callback).toHaveBeenCalled();
  });

  it("passes list arguments to callbacks", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage(
      '{"jsonrpc": "2.0", "method":"some_notification", "params":[1,2]}'
    );
    expect(callback).toHaveBeenCalledWith(1, 2);
  });

  it("passes object argument to callbacks", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage(
      '{"jsonrpc": "2.0", "method":"some_notification", "params":{"foo": "bar", "baz": 42}}'
    );
    expect(callback).toHaveBeenCalledWith({ foo: "bar", baz: 42 });
  });
});

describe("JsonRPCClient calls", () => {
  let lastCall: { method: string; id: string; params?: object };
  const streamer = (payload: string) => {
    lastCall = JSON.parse(payload);
  };
  it("invokes function and returns result", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    const result1 = client.call("foo", { value: 12 });
    expect(lastCall.method).toBe("foo");
    expect(lastCall.params).toEqual({ value: 12 });
    const requestid1 = lastCall.id;
    const result2 = client.call("bar");
    expect(lastCall.method).toBe("bar");
    const requestid2 = lastCall.id;
    // simulate responses in different order
    client.handleMessage(
      JSON.stringify({ jsonrpc: "2.0", result: 12, id: requestid2 })
    );
    client.handleMessage(
      JSON.stringify({ jsonrpc: "2.0", result: 42, id: requestid1 })
    );
    expect(result1).resolves.toEqual(42);
    expect(result2).resolves.toEqual(12);
  });

  it("rejects promise on jsonrpc error", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    const result1 = client.call("foo", { value: 12 });
    expect(lastCall.method).toBe("foo");
    expect(lastCall.params).toEqual({ value: 12 });
    const requestid1 = lastCall.id;
    client.handleMessage(
      JSON.stringify({
        jsonrpc: "2.0",
        error: { code: -321, message: "uhh, something went wrong" },
        id: requestid1,
      })
    );

    return expect(result1).rejects.toStrictEqual({
      code: -321,
      message: "uhh, something went wrong",
    });
  });
});
