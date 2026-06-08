// @ts-check
const esbuild = require("esbuild");

const isWatch = process.argv.includes("--watch");

/** @type {esbuild.BuildOptions} */
const buildOptions = {
  entryPoints: ["./src/extension.ts"],
  bundle: true,
  outfile: "./dist/extension.js",
  external: ["vscode"],
  format: "cjs",
  platform: "node",
  target: "node18",
  sourcemap: true,
  minify: !isWatch,
  logLevel: "info",
};

async function main() {
  if (isWatch) {
    console.log("[esbuild] starting build...");
    const ctx = await esbuild.context(buildOptions);
    await ctx.watch();
    console.log("[esbuild] watching for changes...");
  } else {
    await esbuild.build(buildOptions);
    console.log("[esbuild] build complete.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
