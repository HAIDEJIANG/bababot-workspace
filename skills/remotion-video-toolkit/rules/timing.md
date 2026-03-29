---
name: timing
description: Interpolation curves in Remotion - linear, easing, spring animations
metadata:
 tags: spring, bounce, easing, interpolation

A simple linear interpolation is done using the `interpolate` function.

```ts title="Going from 0 to 1 over 100 frames"
import {interpolate} from 'remotion';

const opacity = interpolate(frame, [0, 100], [0, 1]);
```

By default, the values are not clamped, so the value can go outside the range [0, 1].
Here is how they can be clamped:

```ts title="Going from 0 to 1 over 100 frames with extrapolation"
const opacity = interpolate(frame, [0, 100], [0, 1], {
 extrapolateRight: 'clamp',
 extrapolateLeft: 'clamp',
});

## Spring animations
Spring animations have a more natural motion.
They go from 0 to 1 over time.

```ts title="Spring animation from 0 to 1 over 100 frames"
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

const frame = useCurrentFrame();
const {fps} = useVideoConfig();

const scale = spring({
 frame,
 fps,

### Physical properties
The default configuration is: `mass: 1, damping: 10, stiffness: 100`.
This leads to the animation having a bit of bounce before it settles.

The config can be overwritten like this:

```ts
 config: {damping: 200},

The recommended configuration for a natural motion without a bounce is: `{ damping: 200 }`.

Here are some common configurations:

```tsx
const smooth = {damping: 200}; // Smooth, no bounce (subtle reveals)
const snappy = {damping: 20, stiffness: 200}; // Snappy, minimal bounce (UI elements)
const bouncy = {damping: 8}; // Bouncy entrance (playful animations)
const heavy = {damping: 15, stiffness: 80, mass: 2}; // Heavy, slow, small bounce

### Delay
The animation starts immediately by default.
Use the `delay` parameter to delay the animation by a number of frames.

const entrance = spring({
 frame: frame - ENTRANCE_DELAY,
 delay: 20,

### Duration
A `spring()` has a natural duration based on the physical properties.
To stretch the animation to a specific duration, use the `durationInFrames` parameter.

const spring = spring({
 durationInFrames: 40,

### Combining spring() with interpolate()
Map spring output (0-1) to custom ranges:

const springProgress = spring({

// Map to rotation
const rotation = interpolate(springProgress, [0, 1], [0, 360]);

<div style={{rotate: rotation + 'deg'}} />;

### Adding springs
Springs return just numbers, so math can be performed:

const {fps, durationInFrames} = useVideoConfig();

const inAnimation = spring({
const outAnimation = spring({
 durationInFrames: 1 * fps,
 delay: durationInFrames - 1 * fps,

const scale = inAnimation - outAnimation;

## Easing
Easing can be added to the `interpolate` function:

import {interpolate, Easing} from 'remotion';

const value1 = interpolate(frame, [0, 100], [0, 1], {
 easing: Easing.inOut(Easing.quad),

The default easing is `Easing.linear`.
There are various other convexities:

- `Easing.in` for starting slow and accelerating
- `Easing.out` for starting fast and slowing down
- `Easing.inOut`

and curves (sorted from most linear to most curved):

- `Easing.quad`, `Easing.sin`, `Easing.exp`, `Easing.circle`

Convexities and curves need be combined for an easing function:

Cubic bezier curves are also supported:

 easing: Easing.bezier(0.8, 0.22, 0.96, 0.65),