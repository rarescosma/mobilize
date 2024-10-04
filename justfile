HUB := "docker.io"
DEFAULT_WORKDIR := `pwd` + "/workdir"
DOCKER := "docker run -it --rm --user " + `id -u` + ":" + `id -g`

_default:
  @just --list

# pull image from ghcr.io
pull_ghcr:
    docker pull ghcr.io/rarescosma/mobilize:$(just _version)
    docker tag ghcr.io/rarescosma/mobilize:$(just _version) mobilize:$(just _tag)

# build the docker image
dockerize:
    docker build -f docker/Dockerfile . -t mobilize:$(just _tag)

# convert a single URL to epub+mobi
convert_url url workdir=DEFAULT_WORKDIR:
    mkdir -p "{{workdir}}"
    {{DOCKER}} --entrypoint="mobilize" -v "{{workdir}}":/workdir \
      mobilize:$(just _tag) /workdir "{{url}}"

# watch a directory for .url files and convert them automatically; NOTE: watchdir needs to be an absolute path
watch_dir watchdir outdir="":
    #!/usr/bin/env bash
    test -z "{{outdir}}" && outdir="{{watchdir}}" || outdir="{{outdir}}"
    mkdir -p "{{watchdir}}" "$outdir"

    {{DOCKER}} \
      -e WATCH_DIR="/watchdir" -v "{{watchdir}}":/watchdir \
      -e OUT_DIR="/outdir" -v "$outdir":/outdir \
      mobilize:$(just _tag)

# bump the module version
bump_version part="patch":
    bumpversion patch --verbose setup.py --commit --sign-tags --tag

_version:
    #!/usr/bin/env bash
    py_version="$(grep "version=" setup.py | grep -oE "[0-9\.]+")"
    printf "v%s" $py_version

# hash important files to make a project tag
_tag:
    #!/usr/bin/env bash
    git ls-files -s \
      docker package.json package-lock.json extract_article.js \
      requirements.txt setup.py mobilize watcher.sh \
        | git hash-object --stdin \
        | cut -c-20

# publish the docker image to a private registry
_push_private:
    docker tag mobilize:$(just _tag) {{HUB}}/mobilize:latest
    docker push {{HUB}}/mobilize:latest
