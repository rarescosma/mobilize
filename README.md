# Mobilize

Got a web article that you want converted to `.epub` and/or `.mobi` formats?

Look no further!

## Installation

Since we're depending on wrapped NodeJS modules and `calibre` for the EPUB to
MOBI conversion, I couldn't be bothered to offer any form of a "binary" package
for this.

Just build & use the docker image, it has its batteries.

## Prerequisites:

- [just](https://getbetter.ro/journal/2019-05-31-biking-the-mosel-palatinate/) - the command runner
- [docker](https://docs.docker.com/engine/install/) - the container engine ([podman](https://podman.io/docs/installation) might work too)
- git (ha-HA)

Clone the repo:

```shell
$ git clone https://github.com/rarescosma/mobilize.git
```

Build the docker image:

```shell
$ just dockerize
```

_NOTE:_ you can now use a pre-built docker image from `ghcr.io` if you
want to avoid the local build. Instead of the `just dockerize` command use:

```shell
$ just pull_ghcr
```

## Usage

### Convert a single URL

```shell
$ just convert_url https://en.wikipedia.org/wiki/Haber_process 
```

The output will be produced by default in a subdirectory of your current 
directory: `$(pwd)/workdir`

You can also specify a different output directory:

```shell
$ just convert_url https://en.wikipedia.org/wiki/Haber_process /absolute/path/to/output/dir
```

### Watch a directory for `.url` files and convert them automatically

```shell
$ just watch_dir /absolute/path/to/dir
```

By default the output will be produced in the same directory, but you can also
specify a different output directory:

```shell
$ just watch_dir /absolute/path/to/watched_dir /absolute/path/to/output_dir
```

`.url` files have a very simple syntax:

```
[InternetShortcut]
URL=https://example.com
```

They are usually produced when clicking the "Share" button on an Android phone,
hence the support for them.

The way I use this program is I have it deployed on a server along with
NextCloud. Whenever I don't want to wreck my eyes reading long-form articles
on the phone, I click the "Share" button in Firefox Android, select NextCloud
as the destination and upload the page as an `.url` file.

Then the watcher watching the NextCloud data subdirectory produces the `.mobi`
and `.epub` files that can be synced to the e-reader.

## Credits

I got the original idea and inspiration from a blog post featured on HackerNews:

https://olano.dev/blog/from-rss-to-my-kindle/
