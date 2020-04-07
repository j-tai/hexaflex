# hexaflex

Hexaflexagon generator

## Usage

```
usage: hexaflex.py [-h] [-s SIZE] [-g GAP] [-l LINE_WIDTH] [-x] [-o OUTPUT]
                   [texture [texture ...]]

Create a hexaflexagon template

positional arguments:
  texture               image files to use as textures (default: none)

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE, --size SIZE  (pixels) triangle side length (default: 1024)
  -g GAP, --gap GAP     (pixels) gap between triangles (default: 32)
  -l LINE_WIDTH, --line-width LINE_WIDTH
                        (pixels) thickness of lines (default: 16)
  -x, --hexa            use hexahexaflexagon (6 sides) (default:
                        trihexaflexagon (3 sides))
  -o OUTPUT, --output OUTPUT
                        output filename (default: hexaflex.png)
```

## Examples

```shell
$ hexaflex.py
```

Create a basic tri-hexaflexagon template in `hexaflex.png`.

```shell
$ hexaflex.py image1.png image2.png image3.png
```

Create a tri-hexaflexagon with the three provided images.

```shell
$ hexaflex.py -x image1.png image2.png image3.png image4.png image5.png image6.png
```

Create a hexa-hexaflexagon with the six provided images.

## License

[MIT License](LICENSE).
