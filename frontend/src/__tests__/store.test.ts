import { store } from "../store";
import { api } from "../store/api";

describe("Redux store", () => {
  it("has the correct reducer path", () => {
    expect(api.reducerPath).toBe("api");
  });

  it("configures the store with API middleware", () => {
    const state = store.getState();
    expect(state[api.reducerPath]).toBeDefined();
  });
});
