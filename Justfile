# Create a new Marp presentation: just new my-talk
new slug:
    @printf -- '---\nmarp: true\ntheme: default\npaginate: true\n---\n\n# TODO\n\n**Anže Pečar**\n{{`date +%Y-%m-%d`}}\n\n---\n\n## Slide 2\n\n---\n\n## Thank you!\n' > src/{{`date +%Y-%m-%d`}}-{{slug}}.md
    @echo "Created src/{{`date +%Y-%m-%d`}}-{{slug}}.md"

# Start the Marp dev server with live reload
serve file:
    bunx --bun @marp-team/marp-cli --preview --watch {{file}}
