import { RebootClientProvider } from "@reboot-dev/reboot-react";

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

const url =
  import.meta.env.VITE_APP_CHAT_REBOOT_ENDPOINT || "http://localhost:9991";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RebootClientProvider url={url}>
      <App />
    </RebootClientProvider>
  </React.StrictMode>
);
