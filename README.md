# GNOME Shell
GNOME Shell provides core user interface functions for the GNOME desktop,
like switching to windows and launching applications. GNOME Shell takes
advantage of the capabilities of modern graphics hardware and introduces
innovative user interface concepts to provide a visually attractive and
easy to use experience.

For more information about GNOME Shell, including instructions on how
to build GNOME Shell from source and how to get involved with the project,
see the [project wiki][project-wiki].

## Debian packaging

This tree also provides a Meson target to build a `gnome-shell` Debian
package from the current build directory.

After configuring and building the project, run:

```sh
ninja -C build gnome-shell-deb
```

or:

```sh
ninja -C build deb
```

The generated package is written to the build directory, for example:

```sh
/root/gnome-shell/build/gnome-shell_42.9-0ubuntu2.3_arm64.deb
```

The packaging step reuses the current build outputs, stages the runtime
files that belong to the `gnome-shell` package, maps newly built shared
libraries and typelibs into the package paths expected by the system
package, and then creates a `.deb` with `dpkg-deb`.

Package metadata is copied from the currently installed `gnome-shell`
package by querying `dpkg`. The `Package`, `Version`, `Section`,
`Priority`, `Architecture`, `Maintainer`, `Original-Maintainer`,
`Depends`, `Recommends`, `Suggests`, `Provides`, `Breaks`,
`Description`, and `Homepage` fields are reproduced from the installed
package. `Installed-Size` is recalculated from the newly staged package
contents, and `Conffiles` is written into the generated package control
data.

This target is intended for an already built tree. If the required build
artifacts are missing, run the normal build first and then rerun the
packaging target.

To inspect or install the generated package, use:

```sh
dpkg-deb -c build/gnome-shell_*.deb
sudo dpkg -i build/gnome-shell_*.deb
```

Bugs should be reported to the GNOME [bug tracking system][bug-tracker].
Please refer to the [*Schedule* wiki page][schedule] to see the supported versions.

## Contributing

To contribute, open merge requests at https://gitlab.gnome.org/GNOME/gnome-shell.

Commit messages should follow the [GNOME commit message
guidelines](https://wiki.gnome.org/Git/CommitMessages). We require an URL
to either an issue or a merge request in each commit.

## Default branch

The default development branch is `main`. If you still have a local
checkout under the old name, use:
```sh
git checkout master
git branch -m master main
git fetch
git branch --unset-upstream
git branch -u origin/main
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
```

## License
GNOME Shell is distributed under the terms of the GNU General Public License,
version 2 or later. See the [COPYING][license] file for details.

[project-wiki]: https://wiki.gnome.org/Projects/GnomeShell
[bug-tracker]: https://gitlab.gnome.org/GNOME/gnome-shell/issues
[schedule]: https://wiki.gnome.org/Schedule
[license]: COPYING
