import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { spawn } from "node:child_process";

const chime = "/Users/thinh/.pi/sounds/agent_done_chime.mp3";

export default function (pi: ExtensionAPI) {
  pi.on("agent_settled", () => {
    const player = spawn("/usr/bin/afplay", [chime], {
      detached: true,
      stdio: "ignore",
    });
    player.on("error", () => {});
    player.unref();
  });
}
