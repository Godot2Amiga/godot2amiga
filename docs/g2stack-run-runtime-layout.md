# g2stack run runtime layout fix

The generated startup-sequence now contains only:

```text
DH0:minimal
```

The entire `dist/data/` tree is copied into:

```text
dist/.g2stack-run/DH0/data/
```

`PACKAGE_INFO.json` remains host-side metadata.
