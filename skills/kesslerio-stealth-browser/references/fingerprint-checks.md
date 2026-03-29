# Browser Fingerprint Checks
What anti-bot systems check and how to evade.

## Detection Layers
```
┌─────────────────────────────────────────────┐
│ Layer 1: Network/IP │
│ • IP reputation score │
│ • Datacenter vs residential │
│ • Geo-location consistency │
├─────────────────────────────────────────────┤
│ Layer 2: TLS Fingerprint │
│ • JA3/JA4 hash │
│ • Cipher suite order │
│ • TLS extensions │
│ Layer 3: HTTP Headers │
│ • User-Agent consistency │
│ • Header order │
│ • Accept-Language │
│ Layer 4: Browser Fingerprint │
│ • navigator.webdriver │
│ • Canvas/WebGL hash │
│ • Audio fingerprint │
│ • Font enumeration │
│ Layer 5: Behavioral │
│ • Mouse movements │
│ • Scroll patterns │
│ • Timing analysis │
│ • Click patterns │
└─────────────────────────────────────────────┘

## Specific Checks & Countermeasures

### 1. navigator.webdriver
**What:** `navigator.webdriver` returns `true` for automated browsers.

**Check:**
```javascript
navigator.webdriver // true = bot

**Countermeasure:**
- Nodriver: Automatically patches
- Camoufox: Patched at C++ level
- Playwright-stealth: `delete navigator.webdriver` (weak, can be detected)

### 2. Chrome DevTools Protocol (CDP)
**What:** Presence of CDP side-channels reveals automation.

// Sites check for CDP artifacts
window.cdc_adoQpoasnfa76pfcZLmcfl_Array
window.cdc_adoQpoasnfa76pfcZLmcfl_Promise

- Nodriver: Uses CDP but patches artifacts
- Camoufox: No CDP (native Firefox)
- Patchright: Patches CDP artifacts

### 3. Canvas Fingerprint
**What:** Each GPU/driver combo renders slightly differently.

canvas.toDataURL() // Unique hash per system

- Camoufox: Injects deterministic noise
- Some detection tools look for perfectly identical canvas = bot

### 4. WebGL Fingerprint
**What:** GPU vendor/renderer strings.

gl.getParameter(gl.RENDERER) // "ANGLE (Intel HD Graphics)"
gl.getParameter(gl.VENDOR) // "Google Inc."

- Camoufox: Spoofs to common values
- Avoid VMs with "llvmpipe" or "SwiftShader" (instant bot flag)

### 5. Audio Fingerprint
**What:** AudioContext processing variations.

new AudioContext().createOscillator() // Unique waveform

- Camoufox: Adds noise to audio processing

### 6. Font Enumeration
**What:** Bots often have minimal fonts installed.

// Test if specific fonts render
document.fonts.check('12px "Segoe UI"')

- Install standard fonts in your environment
- Camoufox: Spoofs font list

### 7. Screen/Window Size
**What:** Unusual dimensions = bot.

screen.width, screen.height
window.innerWidth, window.innerHeight

- Use standard resolutions: 1920x1080, 1366x768
- Avoid: 800x600, odd dimensions

### 8. Timezone Consistency
**What:** Timezone must match IP geo-location.

Intl.DateTimeFormat().resolvedOptions().timeZone
new Date().getTimezoneOffset()

- Set timezone to match proxy location:
 ```bash
 TZ="America/New_York" python script.py

### 9. Language Consistency
**What:** Browser language should match geo.

navigator.language // "en-US"
navigator.languages // ["en-US", "en"]

- Configure browser locale to match proxy:
 ```python
 # Camoufox
 async with AsyncCamoufox(locale="en-US") as browser:

### 10. Hardware Concurrency
**What:** VMs often report 1-2 CPUs.

navigator.hardwareConcurrency // 1 or 2 = suspicious

- Camoufox: Spoofs to 4-8
- Or use real hardware, not minimal VM

### 11. Headless Detection
**What:** Multiple signals reveal headless mode.

**Checks:**
navigator.plugins.length === 0
navigator.mimeTypes.length === 0
window.chrome === undefined

- Use "new headless" mode: `headless="new"`
- Or run headed in Xvfb
- Camoufox headless is well-patched

### 12. Mouse/Keyboard Events
**What:** Bots often have no mouse history.

// Sites track mouse movement patterns
document.addEventListener('mousemove', analyze)

- Inject random mouse movements
- Nodriver/Camoufox: Built-in human-like movement
- Don't teleport cursor - use bezier curves

## Test Sites
Check your stealth setup:

- https://bot.sannysoft.com: Comprehensive bot detection
- https://browserleaks.com: All fingerprints
- https://nowsecure.nl: Cloudflare detection
- https://pixelscan.net: Bot detection score
- https://abrahamjuliot.github.io/creepjs: Advanced fingerprinting

## Tool Comparison
webdriver, Camoufox=, Plain Playwright=
CDP artifacts, Camoufox= (no CDP), Plain Playwright=
Canvas, Camoufox=, Plain Playwright=
WebGL, Camoufox=, Plain Playwright=
Audio, Camoufox=, Plain Playwright=
Fonts, Camoufox=, Plain Playwright=
Headless, Camoufox=, Plain Playwright=
TLS, Camoufox=, Plain Playwright=

Legend: = patched, = detected