rm -r dist/
hatch build
twine upload --repository POLARS_ASTRO dist/*