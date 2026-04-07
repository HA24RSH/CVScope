import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders CVScope header", () => {
  render(<App />);
  expect(screen.getByText(/cvscope/i)).toBeInTheDocument();
});
