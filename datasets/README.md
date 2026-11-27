# Optional dataset repositories

Action and constraint checks live in the independently versioned public repository https://github.com/RonBibb/paper-A-action-constraint-checks.

Initialize its pinned checkout after cloning this pipeline:

```sh
git submodule update --init datasets/action-constraint-checks
```

The historical `data/raw/paper-a-20261114/derivation/CHECKS` path is a relative symlink to this checkout. The original collection DATA_MANIFEST.json remains unchanged. A clone without this optional submodule will not have the CHECKS files available and cannot complete collection verification until initialization. Published Git history is preserved; this split does not remove historical bytes or change other datasets.
