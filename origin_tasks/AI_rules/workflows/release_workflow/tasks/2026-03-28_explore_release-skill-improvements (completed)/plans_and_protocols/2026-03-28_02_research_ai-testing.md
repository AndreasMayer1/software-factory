# Research: AI-Driven Testing for Flutter Release Gate

_Task: TASK-PROC-036-09 — Explore Release Skill Improvements_
_Date: 2026-03-28_
_Constraint: Flutter app runs on Windows (outside dev container); Claude Code runs inside WSL2 container_

---

## Key Findings

### 1. LLM-Driven Flutter Integration Tests

**Flutter's own integration test framework (native, no LLM)**

Flutter ships `integration_test` (a package in the SDK) that drives the app on a real device or desktop. The command is:

```bash
flutter test integration_test/           # runs on connected device
flutter test --platform windows          # runs on Windows desktop target
```

This is scriptable from Windows PowerShell and requires no LLM. Tests are Dart code using `testWidgets` + `IntegrationTestWidgetsFlutterBinding`. Flutter 3.22+ explicitly supports `flutter test --platform windows` for desktop targets.

**MCP-based LLM-driven test generation (emerging, 2025–2026)**

Several MCP servers now let an AI coding assistant (Claude Code, Cursor, etc.) interact with a running Flutter app:

| Tool | Description | Status |
|---|---|---|
| `flutter-skill` (ai-dashboad) | 253 MCP tools for E2E testing across Flutter, Android, iOS, web, Windows desktop — zero test code, natural language | Active (2025–2026) |
| `FutterTestMcp` (cape2333) | MCP server that generates and executes Flutter integration tests from natural language descriptions | Active (2025) |
| `mcp_flutter` (Arenukvern) | MCP server exposing widget tree inspection, screenshots, hot reload, error monitoring via Dart VM Service Protocol | Active (March 2025+) |
| `mobile-device-mcp` (saranshbamania) | 49 tools for screenshots, UI inspection, touch interaction, Flutter widget tree inspection | Active (2025) |

The key mechanism: these MCP servers connect to the Dart VM debug service port exposed by a running Flutter app (`--dart-vm-host=localhost --dart-vm-port=8181`). Claude Code (running in WSL2) can reach a Flutter Windows app's Dart VM port if the port is exposed over localhost or TCP.

**Key limitation for Windows desktop**: `mcp_flutter` (Arenukvern) is tested on macOS/iOS; Windows is listed as not yet tested. `flutter-skill` claims cross-platform desktop support including Windows, but community validation for Windows specifically is thin.

**MaestroGPT (AI-assisted YAML test generation)**

Maestro is a YAML-based mobile/Flutter E2E test tool. MaestroGPT is an AI assistant trained on Maestro that generates YAML test flows from natural language prompts. However, Maestro primarily targets Android/iOS via the accessibility layer — it does not currently support Windows desktop Flutter apps. It also requires the app to be on a device/emulator reachable by Maestro CLI, not available for Windows desktop.

---

### 2. Claude as Test Agent

**Pattern A: Claude Code + MCP server + running Flutter app**

Claude Code running in WSL2 can control a Flutter Windows app if:
1. The Flutter app is launched with `--enable-vmservice` (or in debug/profile mode)
2. The Dart VM service port (default 8181) is reachable from WSL2 (via `localhost` forwarding, which WSL2 provides automatically for Windows → WSL2, but the reverse — WSL2 → Windows host — requires the Windows host IP or `host.docker.internal`)
3. An MCP server bridges Claude Code to the Dart VM service

This is the most architecturally native path. Claude Code then calls MCP tools like `get_widget_tree`, `take_screenshot`, `tap_element`, and decides pass/fail based on what it sees.

**Pattern B: Claude API + Computer Use (screenshot-based)**

The Claude API's computer use tool allows a Python script to:
1. Take a screenshot of the running Windows app
2. Send it to the Claude API with a prompt like "Does the app show the main screen? Is there any error visible?"
3. Receive a pass/fail judgment or next action from Claude
4. Optionally click/type via computer use tools

This is platform-independent and does not require Dart VM access. The script runs on Windows (or from WSL2 via Windows screenshot capture). The Python agent loop sends screenshots, Claude responds with actions or verdicts.

The beta header required (as of March 2026): `anthropic-beta: computer-use-2025-11-24` for Claude Sonnet 4.6 / Opus 4.6.

**Pattern C: Screenshot-only (Claude as reviewer, no interaction)**

The simplest variant: build and launch the app, take a screenshot of the main screen, send to Claude API with a prompt. Claude returns a pass/fail verdict. No clicking, no Dart VM. The developer's Windows script captures the screenshot using PowerShell (`Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen`), passes it to a Python script that calls the Claude API, and interprets the result.

This is the lowest-friction path and sufficient for a "does the app launch and show the expected screen" smoke gate.

---

### 3. Computer Use for App Testing

**Current status (March 2026)**

Claude's computer use (in the Claude Desktop app / Cowork) is **macOS only** as of March 2026. Windows support is listed as "coming soon" in official documentation.

However, the **Claude API's computer use tool** is available on all platforms via API calls. It does not depend on the Claude Desktop app. A Python script running on Windows can:
- Use `PIL.ImageGrab.grab()` or PowerShell to capture the screen
- Encode as base64 and send to the Claude API as a `tool_result` for the screenshot tool
- Have Claude analyze the image and return a verdict or next action
- Execute the next action (click, type) via `pyautogui` or PowerShell

**Practical Windows script loop pattern (Claude API computer use)**

```python
import anthropic, base64, io
from PIL import ImageGrab

client = anthropic.Anthropic()

def take_screenshot():
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# Agent loop: send screenshot → Claude decides action → execute → repeat
```

The script launches the Flutter Windows app (`subprocess.Popen(["path/to/app.exe"])`), waits for startup, takes a screenshot, and sends it to Claude with a prompt describing the expected state. Claude returns either "PASS — app shows expected screen" or "FAIL — [reason]".

**Key limitation**: Computer use via API requires calling the Anthropic API (cloud), meaning the Windows machine needs internet access at test time. This is acceptable for a release gate script.

**Existing tooling: `windows-to-wsl2-screenshots` (jddev273)**

This tool automates capturing Windows screenshots and making them available inside WSL2 as file paths. Claude Code in WSL2 can then read those screenshot files directly. This creates a usable bridge for a "Claude reviews screenshots" workflow without needing full computer use.

**Emerging pattern: `os-ai-computer-use` (777genius)**

An open-source desktop app that wraps Anthropic + OpenAI computer use APIs as a ready-to-use automation tool, OS and API agnostic. Can be run on Windows.

---

### 4. Existing AI Testing Tools

**Appium + AI / Appium MCP**

Appium MCP introduces agentic, AI-driven mobile testing: instead of rigid scripts, an AI agent understands application context and dynamically decides how tests execute. It enables LLM-driven test creation and execution for iOS and Android across native, hybrid, and web contexts.

Appium supports Flutter via the `appium-flutter-driver`. However, Appium does not support Flutter Windows desktop targets — it is a mobile-first framework.

**GPT Driver / Mobileboost Appium AI SDK**

An Appium SDK that uses AI (GPT) to handle dynamic selectors and self-heal tests. Same limitation: mobile only (Android/iOS).

**testRigor**

Plain-English test authoring, self-healing, cross-platform. Supports web, mobile, and desktop (via browser). No specific Flutter Windows desktop support documented.

**TestSprite**

Fully autonomous testing agent covering planning, test generation, execution, and root-cause analysis. Integrates via MCP. Web and API focused; desktop app support not explicitly documented for Flutter Windows.

**LELANTE (academic, 2025)**

Research paper: "LEveraging LLM for Automated ANdroid TEsting" — LLM-driven execution that interprets human-language test cases without pre-written scripts, targeting Android specifically.

**flutter-skill (ai-dashboad) — most relevant for this project**

Of all tools found, `flutter-skill` most directly addresses the use case:
- Claims support for Flutter + Windows desktop (listed alongside Android, iOS, web)
- 253 MCP tools including screenshots, tap, scroll, text input, element finding
- Zero test code required — natural language descriptions
- Works with Claude, Cursor, Windsurf, Copilot
- Connects to running app; does not require Dart VM debug mode for interaction (uses accessibility APIs)

Caveat: the tool is relatively new (2025–2026) and Windows desktop support is less documented than mobile/web.

---

### 5. Practical Windows Script Pattern

**Two realistic architectures for this project**

#### Architecture A: PowerShell script → Flutter integration test (no LLM)

The simplest and most robust path. A PowerShell script on Windows:

```powershell
# 1. Build the Windows release candidate
cd C:\path\to\flutter_app
flutter build windows --release

# 2. Run integration tests against the Windows target
flutter test integration_test\smoke_test.dart --platform windows

# 3. Report result
if ($LASTEXITCODE -eq 0) { Write-Host "PASS" } else { Write-Host "FAIL"; exit 1 }
```

Tests are pre-authored Dart integration tests. No LLM needed at test-run time. This is the production-grade, deterministic approach. The developer writes the smoke tests once; the script runs them on every release.

**Verdict for smoke gate**: Feasible today. Requires writing the Dart integration test file once. Fully automated, deterministic, runs in ~30 seconds for a basic smoke test.

#### Architecture B: PowerShell script → launch app → Claude API reviews screenshots

A Python/PowerShell script that:
1. Builds and launches the Flutter Windows app
2. Takes a screenshot after a startup delay
3. Sends the screenshot to the Claude API with a structured prompt
4. Claude returns PASS/FAIL + reason
5. Script exits 0 (pass) or 1 (fail)

```python
# Simplified pseudocode — runs on Windows with Anthropic API key
import subprocess, time, anthropic, base64, io
from PIL import ImageGrab

subprocess.Popen([r"build\windows\x64\runner\Release\app.exe"])
time.sleep(5)  # wait for startup

img = ImageGrab.grab()
buf = io.BytesIO(); img.save(buf, "PNG")
screenshot_b64 = base64.b64encode(buf.getvalue()).decode()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}},
            {"type": "text", "text": (
                "This is a screenshot of a Flutter mood tracker app after launch. "
                "Respond with exactly 'PASS' if the main screen is visible and no error dialog is shown. "
                "Respond with 'FAIL: <reason>' if there is an error, crash, or blank screen."
            )}
        ]
    }]
)
verdict = response.content[0].text.strip()
print(verdict)
exit(0 if verdict.startswith("PASS") else 1)
```

**Verdict for smoke gate**: Feasible today using the Claude API with vision (not computer use — just image input). No special beta headers needed for image-only analysis. Cost: ~$0.003 per screenshot check at Sonnet 4 pricing. Requires Anthropic API key on the Windows machine.

#### Architecture C: Claude Code in WSL2 + MCP Flutter server + Windows app

Claude Code (running in WSL2) connects to the running Flutter Windows app via `flutter-skill` or `mcp_flutter` MCP server. Claude drives the app through MCP tools, takes screenshots, asserts state.

**Verdict for smoke gate**: Experimentally feasible but has open questions:
- WSL2 → Windows host port forwarding for Dart VM service requires explicit configuration
- `flutter-skill` Windows desktop support is claimed but not well-documented in community reports
- Requires the MCP server running on the Windows side (or a WSL2-accessible port)
- Non-trivial setup for a CI/release gate context

---

## Feasibility Assessment

| Approach | Feasibility Today | Effort | Recommendation |
|---|---|---|---|
| Flutter `integration_test` (Dart, `--platform windows`) | High — supported since Flutter 3.22 | Low (write tests once) | Recommended as primary automated gate |
| Claude API vision review (screenshot → pass/fail) | High — image input works with standard API | Low–Medium (Python script, ~50 lines) | Recommended as LLM augmentation layer |
| `flutter-skill` MCP + Claude Code in WSL2 | Medium — Windows desktop support experimental | High (MCP setup, port forwarding, debugging) | Future option, not production-ready for release gate |
| Maestro + AI (YAML flows) | Low for Windows desktop — mobile/Android/iOS only | N/A | Not applicable to Windows desktop target |
| Appium + AI | Low for Windows desktop — mobile only | N/A | Not applicable to Windows desktop target |
| Claude Computer Use (Desktop app) | Low — macOS only in Desktop app | N/A | Not available on Windows until Desktop app adds Windows support |
| Claude Computer Use (API-driven, Python script) | Medium — works via API but requires careful screenshot loop | Medium | Viable for interactive multi-step testing; overkill for basic smoke gate |
| `mcp_flutter` (Arenukvern) | Low for Windows — tested macOS/iOS only | High | Not recommended until Windows support confirmed |

---

## Recommendation

### Recommended approach: Two-layer smoke gate

**Layer 1 (deterministic): Pre-authored Flutter integration test**

Write a `integration_test/smoke_test.dart` that covers the 3–5 most critical flows (app launch, main screen visible, navigation to key screens). Run it via:

```powershell
flutter test integration_test\smoke_test.dart --platform windows
```

This runs in ~30 seconds, is fully deterministic, requires no API key or internet access, and provides a binary pass/fail exit code. The test is written once and maintained alongside the app.

This is the **primary gate** in the release script. If it fails, release is blocked.

**Layer 2 (LLM augmentation): Claude API screenshot review**

After Layer 1 passes, a Python script launches the release build (`flutter build windows --release`), takes a screenshot, and asks Claude (via API, image input, no computer use) to confirm visual appearance. This catches regressions that integration tests miss (visual corruption, wrong colors, layout breakage).

This is the **secondary gate** — it augments but does not replace Layer 1. Output is shown to the developer for awareness; policy on whether it blocks release is configurable.

### What is NOT recommended for this project right now

- MCP-based Claude Code control of the Windows app — too experimental, too much WSL2 ↔ Windows networking complexity for a reliable release gate
- Maestro or Appium — not applicable to Flutter Windows desktop
- Claude Desktop computer use — macOS only

### Integration with the `/release` skill

The release skill's Phase 2 (Build + Test + Coverage) can incorporate:

1. `flutter test integration_test\smoke_test.dart --platform windows` — run from Windows PowerShell (or instruct the developer to run it and confirm result)
2. (Optional) Run the Claude API screenshot script — developer runs on Windows, pastes verdict into the release skill prompt
3. The existing manual confirmation gate ("type 'proceed' to continue") remains as the final human sign-off, informed by both automated results

The constraint (Claude Code runs in WSL2, app runs on Windows) means the release skill cannot directly launch the Windows app. The practical model is:
- The skill instructs the developer to run a provided script on Windows
- The developer reports the result (or the script outputs to a shared file that WSL2 can read)
- The skill waits for confirmation before proceeding to Phase 3

A dedicated `scripts/smoke_test_windows.ps1` (PowerShell) + `scripts/smoke_test_llm.py` (Python, Claude API) pair would implement both layers. The release skill references these scripts and waits for the developer's report.

---

## Sources

- [Flutter integration testing docs — docs.flutter.dev](https://docs.flutter.dev/testing/integration-tests)
- [Desktop support for Flutter — docs.flutter.dev](https://docs.flutter.dev/platform-integration/desktop)
- [Build and release a Windows desktop app — docs.flutter.dev](https://docs.flutter.dev/deployment/windows)
- [flutter-skill — GitHub (ai-dashboad)](https://github.com/ai-dashboad/flutter-skill)
- [flutter-skill — Awesome MCP Servers](https://mcpservers.org/servers/ai-dashboad/flutter-skill)
- [Zero-code E2E testing for any app with OpenClaw + flutter-skill — DEV Community](https://dev.to/charlieww/zero-code-e2e-testing-for-any-app-with-openclaw-flutter-skill-f00)
- [FutterTestMcp — GitHub (cape2333)](https://github.com/cape2333/FutterTestMcp)
- [mcp_flutter — GitHub (Arenukvern)](https://github.com/Arenukvern/mcp_flutter)
- [Integrating mcp_flutter into Claude Code — GitHub Gist](https://gist.github.com/lukemmtt/62c0889f7a959546702a973239382b12)
- [Flutter Inspector MCP Server — Glama](https://glama.ai/mcp/servers/@Arenukvern/mcp_flutter)
- [mobile-device-mcp — Glama](https://glama.ai/mcp/servers/saranshbamania/mobile-device-mcp)
- [7 MCP Servers Every Dart and Flutter Developer Should Know — Very Good Ventures](https://verygood.ventures/blog/7-mcp-servers-every-dart-and-flutter-developer-should-know/)
- [Computer use tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Computer Use API: Desktop Automation Guide — digitalapplied.com](https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide)
- [Claude's Computer Use API: Complete Tutorial — Medium (Gaston Aps, Feb 2026)](https://medium.com/@gastonaps/claudes-computer-use-api-complete-tutorial-for-ai-powered-desktop-automation-47f6034f5c0a)
- [Let Claude use your computer in Cowork — Claude Help Center](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)
- [Teaching Claude Code to See in Windows — Medium (Alex Filiakov)](https://medium.com/@alexfiliakov/teaching-claude-code-to-see-in-windows-automating-ui-development-with-screenshots-in-wsl-52b98b8c1836)
- [windows-to-wsl2-screenshots — GitHub (jddev273)](https://github.com/jddev273/windows-to-wsl2-screenshots)
- [Maestro Flutter integration testing — maestro.dev](https://maestro.dev/insights/maestro-flutter-integration-testing)
- [MaestroGPT — maestro.dev](https://maestro.dev/)
- [Appium MCP for AI-Driven Mobile Testing — getpanto.ai](https://www.getpanto.ai/blog/appium-mcp-for-mobile-app-qa-testing)
- [How AI and Appium Are Revolutionizing Mobile Testing in 2026 — metadesignsolutions.com](https://metadesignsolutions.com/how-ai-appium-is-changing-mobile-testing-in-2026/)
- [LELANTE: LEveraging LLM for Automated ANdroid TEsting — arXiv](https://arxiv.org/html/2504.20896v1)
- [testRigor Flutter Testing](https://testrigor.com/flutter-testing/)
- [TestSprite Autonomous Testing](https://www.testsprite.com/)
- [Flutter automated screenshot testing — Codemagic Blog](https://blog.codemagic.io/flutter-automated-screenshot-testing/)
- [Dart and Flutter MCP server — docs.flutter.dev](https://docs.flutter.dev/ai/mcp-server)
- [MCP Servers for Dart and Flutter Developers 2026 — VoxturrLabs](https://voxturrlabs.com/blog/mcp-servers-for-dart-and-flutter-developers-2026/)
