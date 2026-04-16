# Create a new Marp presentation: just new my-talk
new slug:
    @printf -- '---\nmarp: true\ntheme: default\npaginate: true\n---\n\n# TODO\n\n**Anže Pečar**\n{{`date +%Y-%m-%d`}}\n\n---\n\n## Slide 2\n\n---\n\n## Thank you!\n' > src/{{`date +%Y-%m-%d`}}-{{slug}}.md
    @echo "Created src/{{`date +%Y-%m-%d`}}-{{slug}}.md"

# Start the Marp dev server with live reload
serve:
    bunx --bun @marp-team/marp-cli --html --server --watch -I src

# Build static site to _site/
build:
    bunx --bun @marp-team/marp-cli --html -I src -o _site
    cp index.html _site/index.html
    cp *.pdf _site/ 2>/dev/null || true
    cp -r src/assets _site/assets 2>/dev/null || true
