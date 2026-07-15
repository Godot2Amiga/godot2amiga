# M7.6c.2c — Animated Main Loop Codegen

Composes the existing animation units into one deterministic C fragment bundle:

- animation and sprite-instance types;
- unique bitmap declarations and loading;
- frame tables;
- bitmap pointer tables;
- sprite instances;
- tick loop;
- clipped current-frame blits;
- reverse-order cleanup.

This delivery does not patch the existing ACE main template yet.
M7.6c.2d performs the final integration and FS-UAE verification.
