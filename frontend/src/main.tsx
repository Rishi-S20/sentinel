import React, { Suspense } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { StackProvider, StackTheme } from "@stackframe/stack";
import { stackClientApp } from "./stack/client";
import App from "./App";
import Loading from "./loading";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <StackProvider app={stackClientApp}>
        <StackTheme>
          <Suspense fallback={<Loading />}>
            <App />
          </Suspense>
        </StackTheme>
      </StackProvider>
    </BrowserRouter>
  </React.StrictMode>
);
