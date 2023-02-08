# Electronique Digitale II
*__Groupe 2TL1 - 4__*

## Setting up

### With Nix

> You will need to [install nix](nixos.org/download), which is safe to install
> alongside your usual package manager (if any).

The devshell provides a python 3.10 interpreter, the [black](TODO) code formatter,
the micropython implementation and its remote shell [rshell](https://github.com/dhylands/rshell/blob/master/README.rst);
and generally a suitable reproducible environment for hacking around.

To enter the devshell, run:

```
nix develop github:austreelis/2tl1-elec-digi2
```

## Useful links

[Raspberry Pi Pico Python SDK documentation](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf)
