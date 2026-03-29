---
name: measuring-text
description: Measuring text dimensions, fitting text to containers, and checking overflow
metadata:
 tags: measure, text, layout, dimensions, fitText, fillTextBox

# Measuring text in Remotion

## Prerequisites
Install @remotion/layout-utils if it is not already installed:

```bash
npx remotion add @remotion/layout-utils # If project uses npm
bunx remotion add @remotion/layout-utils # If project uses bun
yarn remotion add @remotion/layout-utils # If project uses yarn
pnpm exec remotion add @remotion/layout-utils # If project uses pnpm
```

## Measuring text dimensions
Use `measureText()` to calculate the width and height of text:

```tsx
import { measureText } from "@remotion/layout-utils";

const { width, height } = measureText({
 text: "Hello World",
 fontFamily: "Arial",
 fontSize: 32,
 fontWeight: "bold",
});

Results are cached - duplicate calls return the cached result.

## Fitting text to a width
Use `fitText()` to find the optimal font size for a container:

import { fitText } from "@remotion/layout-utils";

const { fontSize } = fitText({
 withinWidth: 600,
 fontFamily: "Inter",

return (
 <div
 style={{
 fontSize: Math.min(fontSize, 80), // Cap at 80px
 }}
 >
 Hello World
 </div>
);

## Checking text overflow
Use `fillTextBox()` to check if text exceeds a box:

import { fillTextBox } from "@remotion/layout-utils";

const box = fillTextBox({ maxBoxWidth: 400, maxLines: 3 });

const words = ["Hello", "World", "This", "is", "a", "test"];
for (const word of words) {
 const { exceedsBox } = box.add({
 text: word + " ",
 fontSize: 24,
 if (exceedsBox) {
 // Text would overflow, handle accordingly
 break;
 }

## Best practices
**Load fonts first:** Only call measurement functions after fonts are loaded.

import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily, waitUntilDone } = loadFont("normal", {
 weights: ["400"],
 subsets: ["latin"],

waitUntilDone().then(() => {
 // Now safe to measure
 const { width } = measureText({
 text: "Hello",
 fontFamily,
})

**Use validateFontIsLoaded:** Catch font loading issues early:

measureText({
 fontFamily: "MyCustomFont",
 validateFontIsLoaded: true, // Throws if font not loaded

**Match font properties:** Use the same properties for measurement and rendering:

const fontStyle = {
 fontWeight: "bold" as const,
 letterSpacing: "0.5px",
};

 ...fontStyle,

return <div style={fontStyle}>Hello</div>;

**Avoid padding and border:** Use `outline` instead of `border` to prevent layout differences:

<div style={{ outline: "2px solid red" }}>Text</div>