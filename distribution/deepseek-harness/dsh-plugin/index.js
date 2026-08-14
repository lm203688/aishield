// dsh-aishield — minimal Cordis plugin entry (DeepSeek Harness, dev preview)
//
// STATUS: skeleton. The *declaration* half (package.json `dsh.bundle.patch`
// + cordis.patch.yml) is stable and enough to be installable via
// `dsh plugin --profile web add dsh-aishield`. The *service/command* half
// below is intentionally minimal because DSH's Cordis service & command API
// is still in flux (developer preview, breaking changes expected). Fill in
// the scan integration once the DSH tool/command registration API stabilizes.
//
// HARD INVARIANT (matches AIShield core): this plugin NEVER runs code from the
// plugin it is asked to scan. It calls OUR scanner (`python -m scanner.cli`)
// against a target path. The target's own code is never executed.

export const name = "aishield";

/**
 * @param {import('cordis').Context} ctx
 * @param {{ python?: string }} [config]
 */
export function apply(ctx, config = {}) {
  const python = config.python ?? "python";

  // Register a service other plugins / the agent can call to scan a plugin
  // before installing it. The exact DSH registration call depends on the
  // stabilized service API — placeholder below, do not ship as-is.
  //
  // ctx.on("aishield/scan-request", async (pluginPath) => {
  //   const { spawn } = await import("node:child_process");
  //   // run OUR scanner on the TARGET path (read-only inference)
  //   const proc = spawn(python, [
  //     "-m", "scanner.cli", "scan",
  //     "--type", "mcp",
  //     "--source", pluginPath,
  //   ]);
  //   // collect stdout -> 4D score + OWASP mapping, return to caller
  // });

  ctx.on("ready", () => {
    console.log("[dsh-aishield] loaded — supply-chain scanner ready (MCP bridge: aishield-mcp-server).");
  });
}
