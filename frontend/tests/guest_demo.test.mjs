import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import esbuild from "esbuild";
import React from "react";
import ReactDOMServer from "react-dom/server";
import { MemoryRouter } from "react-router-dom";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(__dirname, "..");
globalThis.React = React;

// Helper to bundle and load a TSX component using esbuild
function loadComponent(relPath, exportName) {
  const fullPath = path.resolve(frontendRoot, relPath);
  const result = esbuild.buildSync({
    entryPoints: [fullPath],
    bundle: true,
    write: false,
    format: "cjs",
    packages: "external",
    define: {
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify("http://127.0.0.1:8000"),
    },
  });

  const mod = { exports: {} };
  const requireShim = (moduleName) => {
    if (moduleName.startsWith(".")) {
      const resolved = path.resolve(path.dirname(fullPath), moduleName);
      return require(resolved);
    }
    const mod = require(path.resolve(frontendRoot, "node_modules", moduleName));
    if (moduleName === "axios") {
      return mod.default || mod;
    }
    return mod;
  };

  const fn = new Function("module", "exports", "require", result.outputFiles[0].text);
  fn(mod, mod.exports, requireShim);
  return mod.exports[exportName];
}

const GuestDemoPage = loadComponent("src/pages/GuestDemoPage.tsx", "GuestDemoPage");
const LandingPage = loadComponent("src/pages/LandingPage.tsx", "LandingPage");

test("Landing-page guest CTA is visible and points to /demo", () => {
  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(
      MemoryRouter,
      { initialEntries: ["/"] },
      React.createElement(LandingPage)
    )
  );

  // Prominent hero CTA
  assert.match(
    html,
    /href="\/demo"[^>]*>[\s\S]*?Get Started as Guest/,
    "Hero must have a prominent 'Get Started as Guest' button linking to /demo"
  );

  // Top navigation CTA
  assert.match(
    html,
    /href="\/demo"[^>]*>Try Demo/,
    "Top header must include a 'Try Demo' button linking to /demo"
  );

  // Existing auth actions preserved
  assert.match(html, /href="\/login"/, "Login link must be available");
  assert.match(html, /href="\/signup"/, "Signup link must be available");
});

test("Guest demo page renders without authentication and displays disclaimer", () => {
  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(
      MemoryRouter,
      { initialEntries: ["/demo"] },
      React.createElement(GuestDemoPage)
    )
  );

  // Disclaimer banner
  assert.match(
    html,
    /Demo Data — Not a Live AI Analysis/,
    "Disclaimer banner must clearly state 'Demo Data — Not a Live AI Analysis'"
  );
  assert.match(
    html,
    /No live AI requests,[\s\S]*?Git clones,[\s\S]*?or database writes were executed/,
    "Disclaimer banner must explain that no live AI inference or writes occurred"
  );
});

test("Guest demo page displays scores, findings, and remediation details", () => {
  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(
      MemoryRouter,
      { initialEntries: ["/demo"] },
      React.createElement(GuestDemoPage)
    )
  );

  // Scores
  assert.match(html, /68/, "Overall score 68 must be rendered");
  assert.match(html, /Security/, "Security dimension score must be rendered");
  assert.match(html, /Performance/, "Performance dimension score must be rendered");
  assert.match(html, /Maintainability/, "Maintainability dimension score must be rendered");
  assert.match(html, /Readability/, "Readability dimension score must be rendered");

  // Severities
  assert.match(html, /critical/i, "Critical severity finding must be present");
  assert.match(html, /high/i, "High severity finding must be present");
  assert.match(html, /medium/i, "Medium severity finding must be present");
  assert.match(html, /low/i, "Low severity finding must be present");

  // Specific finding content
  assert.match(html, /Dangerous dynamic evaluation via eval\(\)/, "eval finding comment must be present");
  assert.match(html, /shell=True/, "subprocess finding comment must be present");
  assert.match(html, /Remediation Recommendation/, "Remediation recommendation header must be present");

  // Line numbers
  assert.match(html, /Line 14/, "Line 14 badge must be present");
  assert.match(html, /Line 22/, "Line 22 badge must be present");
  assert.match(html, /Line 31/, "Line 31 badge must be present");
  assert.match(html, /Line 39/, "Line 39 badge must be present");
});

test("Guest demo provides clear conversion paths to signup and login", () => {
  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(
      MemoryRouter,
      { initialEntries: ["/demo"] },
      React.createElement(GuestDemoPage)
    )
  );

  // Conversion links
  assert.match(html, /href="\/signup"/, "Conversion link to /signup must be present");
  assert.match(html, /href="\/login"/, "Conversion link to /login must be present");
  assert.match(html, /href="\/"/, "Return to Home link must be present");
  assert.match(html, /Create Free Account/, "'Create Free Account' button must be present");
});

test("Guest demo is strictly isolated and does not import or invoke protected API endpoints", () => {
  const filePath = path.resolve(frontendRoot, "src/pages/GuestDemoPage.tsx");
  const fileContent = fs.readFileSync(filePath, "utf-8");

  // Assert no imports from api services
  assert.doesNotMatch(
    fileContent,
    /from\s+["']\.\.\/api\/(reviews|submissions|repositoryReview|repositoryPdf)["']/,
    "GuestDemoPage must NOT import protected backend API caller functions"
  );

  // Assert no apiClient direct usage
  assert.doesNotMatch(
    fileContent,
    /apiClient/,
    "GuestDemoPage must NOT access apiClient directly"
  );
});

test("Vercel SPA fallback rewrite is configured for /demo, /login, and /signup", () => {
  const vercelConfigPath = path.resolve(frontendRoot, "vercel.json");
  assert.equal(fs.existsSync(vercelConfigPath), true, "frontend/vercel.json must exist");

  const vercelConfig = JSON.parse(fs.readFileSync(vercelConfigPath, "utf-8"));
  assert.equal(Array.isArray(vercelConfig.rewrites), true, "rewrites array must be defined");
  assert.equal(
    vercelConfig.rewrites.some(
      (r) => r.source === "/(.*)" && r.destination === "/index.html"
    ),
    true,
    "SPA fallback rewrite from /(.*) to /index.html must be present"
  );
});
