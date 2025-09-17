[![release](https://github.com/limakzi/smallantimagmas/actions/workflows/release-bump.yaml/badge.svg)](https://github.com/limakzi/smallantimagmas/actions/workflows/release-bump.yaml)

## smallantimagmas

A library of antiassociative magmas of small order.


### Installation

* Simply use [`packagemanager`](1).

```
gap> LoadPackage("packagemanager");
true

gap> InstallPackage("https://github.com/limakzi/smallantimagmas.git");
#I  Created directory /home/limakzi/.gap/
#I  Created directory /home/limakzi/.gap/pkg/
#I  Cloning to /home/limakzi/.gap/pkg/smallantimagmas ...
#I  Package cloned successfully
#I  Checking dependencies for smallantimagmas...
#I    GAPDoc 1.5: true
#I  Building documentation (using makedoc.g)...
Extracting manual examples for smallantimagmas package ...
1 chapters detected
Chapter 1 : extracted 20 examples
true
gap> 
```

* _Alternative_; just put `smallantimagmas` package in your `pkgs` directory.


### Prover9

To classify all antimagmas, one can use `mace4`.

```
mace4 < ./.prover9/antimagma.in
```

To classify all antimagmas up to the isomorphism.

```
mace4 < ./.prover9/antimagma.in | interpformat standard > antimagma.interps
isofilter < antimagma.interps > antimagma.interps_uptoisomorphism
```

---

[1]: https://github.com/gap-packages/PackageManager