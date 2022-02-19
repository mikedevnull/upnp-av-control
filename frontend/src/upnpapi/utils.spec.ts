import { adaptTo } from "./utils";

type Nested = {
  someToken: string;
};

type TestType = {
  someDataValue: number;
  anotherID: number;
  BadStyleButWorks: boolean;
  nested: Nested[];
};

describe("utils", () => {
  it("should adapt snake-case to camel-case", () => {
    const result = adaptTo<TestType>({
      "some-data-value": 42,
      anotherID: 1234,
      "Bad-Style-But-Works": true,
      nested: [{ "some-token": "foo" }, { "some-token": "bar" }],
    });

    expect(result).toStrictEqual({
      someDataValue: 42,
      anotherID: 1234,
      BadStyleButWorks: true,
      nested: [{ someToken: "foo" }, { someToken: "bar" }],
    });
  });
});
