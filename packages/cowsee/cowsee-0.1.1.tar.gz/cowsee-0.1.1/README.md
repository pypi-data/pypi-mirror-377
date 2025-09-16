# cowsee
"A picture is worth a thousand words." -the cow

Visualize geometry data in the command line, along with the famous [talking cow](https://github.com/cowsay-org/cowsay).

```console
$ cowsee hello_world.shp
╔════════════════════════════════════════════════════════════════════════════╗                    
║                                                                            ║
║                      /─\   /─┬─╴                                           ║
║              /─┬┬┬┬┬─┴─┴─┬─┴╴\──┬─╴    ╶──╴  ╶──┬┬╴╶─╴/────\   /┬┬╴        ║
║   ╷ /────┬───┴┬┼┼┼┼┼┬─┬─\\┬╴   /┴╴     /┬┬┬─\╷/┬┴┴┬┬┬─/  ╶─┴───┴┴┴─────\   ║
║   \─┼╴ ╷╷|    \┴┴┴┼┴┴┬┴┬┴╴\┬┬──/╶─╴  /┬┼┼┤├─┴┴┴/  \┴/              /┬╴//   ║
║    ╶┼──┴┴┴─┬\     \─\├╴\─\ \/      /\\┼┼┴┼┴\    /──┬\          /┬──┼┼─/    ║
║   ╶─/      \┼───────┼/ /┬┼\       ╶┴┼─┼┼┬┼┬┼\ /┬/  ╵\┬┬─────┬─┬┼┼╴╷\/      ║
║             |       \─┬┴┴/╵        /┴┬┼┼┼┼┼┴┴┬┼┼─┬┬┬─/\─────┼┬┼/├╴╵        ║
║             \─\      //        ╶╴  ├┬┴┼┼┴┼┴┬┬┴┼┴┬┴┼┼\      ╶┤\┼─/          ║
║              ╶┴┬┬─┬──┼\          ╶┬┼┤ ├┼─┼─┼┼─┼┬┼┬┼/\─┬┬\   |╶/            ║
║      ╶╴        \┴┬┴┬─┴┼┬\        //├┴┬┴┼─┼─┴┼┬┼┼/╵\\ /┴┼┼┬──┤              ║
║                  \─┴\ ├┼┼\       \┬┼┬┼─┼╴| /┴┼┼/   |///┴┼┼╴ ├\             ║
║                     \┬┴┼┼┼┬\      \┴┴┴┬┼┬┴┬┼─┼┤    ├/ \┬┼┼\/┴┤    ╶╴ ╶╴    ║
║    ╷                 ├─┼/\┴┴─\        \┼┤ ├┴┬┴/    ╵   \┼┼┴┼┬┼┬┬┬\╷   ╶╴   ║
║    ╵     ╶╴          |╶┼\    ├╴        ├┴\├\|╶╴         \┴─┴┼┴/\┼┴/╶\╷     ║
║   \╶╴  ╶╴            \─┤\\   |         ├┬┼┼┼┤/\             ├───┴\  ╵╵ ╷   ║
║   ╵      ╶╴            ├─┼\/─/         |├┼┴┼/||           /┬/    \\ ╶─╴╵   ║
║                       /┤ ├┼/           \┼/// \/           \┤ /\   |        ║
║                       ||/┴/             \─/                \─/\─┬─/   /\   ║
║                       ├┼/                                       \╴   /┴/   ║
║                       ├┼╴    ╷                                       ╵     ║
║                       \┴╴ ╷  \╴                                            ║
║                        /─┬/                  /───\  /─────────────\        ║
║          /─────────────/╶┤      /────────────/   \──/             \─┬─╴    ║   ^__^
║   /──────/               \──────/                                   \──\   ║   (oo)\_______
║   ├┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┤   ║   (__)\       )\/\
║                                                                            ║       ||----w |
╚════════════════════════════════════════════════════════════════════════════╝       ||     ||
```

> [!NOTE]  
> `cowsee` requires a monospaced font to be properly displayed without looking real funky.

## Try

If you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, give it a spin with `uvx` and say "hello, world!"

```
uvx cowsee https://international.ipums.org/international/resources/gis/IPUMSI_world_release2024.zip
```

## Install

You can install `cowsee` into your python environment with [uv](https://docs.astral.sh/uv/getting-started/installation/) or [pip](https://pypi.org/project/cowsee/).

`uv add cowsee`

`pip install cowsee`

## Run

To run, it is as simple as:

```
cowsee <filepath/url>
```

Any file type or url that can be input into the `filename` argument of 
[geopandas.read_file()](https://geopandas.org/en/v1.1.1/docs/reference/api/geopandas.read_file.html) 
can be handled by `cowsee`.

Supports visualization of Polygon, LineString, and Point data.

To output a larger or smaller image, the maximum width can be defined using the `--width` or `-w` flag.

Complex Line and Polygon geometries can sometimes visually benefit from some simplification before drawing. 
This can be achieved by adding the `--simplify-ratio` or `-s` flag followed by the ratio number. For example,
`-s 0.5` simplifies geometries to 50% of a text character's equivalent geometric width. 

Finally, if you don't want to see the cow (said no one, ever) you can pass the `--no-cow` flag.

## Looking Ahead

- Testing coverage
- Raster data support
