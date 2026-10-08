# Match a video reference

Use the reference to guide style; drive the result from the chosen music file.

- Inspect at least a quiet and a loud moment, plus adjacent frames when motion is
  relevant. Record observed bar count, color endpoints, width/gap ratio, baseline,
  mirrored versus one-sided geometry, and relative maximum height.
- For timestamps, use local FFmpeg frame extraction, for example:
  `ffmpeg -nostdin -v error -ss 2 -i "/path/reference.mp4" -frames:v 1 "/path/task-owned/frame-2.png"`.
  Choose times within the actual clip and new output names. A supplied screenshot
  does not establish motion or audio-frequency mapping.
- Translate measurements into normalized style fields. Keep color estimates and
  timing estimates labeled as approximations; antialiasing, grading and compression
  can change visible colors. Use the proposed preset and sample as the review surface.
- If a reference has curves/radial geometry/glow, explain the supported bar
  approximation before rendering. Do not present unsupported fields as active.
- Never infer video contents from a URL title. If a link cannot be accessed through
  authorized tools, ask for a local clip or screenshots. Do not bypass site access
  restrictions or download unrequested private material.
- After rendering, check both a light and dark background and several timestamps;
  black in a generic video player can simply mean it does not display alpha.
  Editor compatibility should be tested with the actual sample in the user's
  version. Exporting the MOV as ordinary H.264/MP4 removes transparency.
