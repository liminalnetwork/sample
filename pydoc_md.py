# Liminal Network heavily modified TextRepr, TextDoc, HTMLRepr, and HTMLDoc
# from Python's pydoc module. This file is licensed under:
#   PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# which can be read:
#   https://github.com/python/cpython/blob/main/LICENSE


__doc__ = """
Q: What the heck is this module?
A1: A pydoc generator for markdown.
A2:
Dependencies changed, bootstrapped building stopped working. After
3 hours of debugging and still getting the same error (only seen in sphinx
source, no one else ever posted about the error), we stopped fighting
and embraced pydoc. Removed about 30+ dependent packages for generating
markdown, replaced with this module and a Python stdlib dependency.

Q: Why not just use something else that does this already?
A:
See the answer to the first question, people keep changing stuff, which breaks
super simple stuff. Like generating basic docs in a Markdown file. Pydoc to
text was pretty close to markdown already. If we were super pedantic, could
have left most of the html stuff, as html is valid Markdown... but that makes
for ugly markdown.

Q: But dude, there are packages that do this already on pypi...
A:
We keep going around in circles here, this one module does 3 things:
1. Outputs Markdown versions of a pydoc from the dotted module name
2. If .md file names are provided on the command line, will package them
   into a .tar file and send to stdout
3. If --stdin is provided, will take stdin as a tarfile of .py files for
   documentation, packing the .md output as a .tar sent to stdout

Q: Wait, why spew to a tar file?
A:
`docker save` is great, but having to dig through 1+ gig tar dumps to
extract 40k of docs is slow. This cuts doc build time to <20 seconds, even
on platter-based USB drives. Check the Makefile for details where we pipe
a tar file of source code in, and get a tar file of docs out.

"""

__author__ = (
    "Josiah Carlson, after modifying existing pydoc.py Text and Html formatting"
)

import argparse
import builtins
from collections import deque
import inspect
import io
import os
import re
import sys
import tarfile
import tempfile
import urllib

from pydoc import (
    visiblename,
    Repr,
    Doc,
    pkgutil,
    resolve,
    describe,
    cram,
    stripid,
    getdoc,
    isdata,
    classname,
    classify_class_attrs,
    sort_attributes,
    replace,
    parentname,
)


# these won't import nicely, so let's force them
import pydoc

_getargspec = pydoc._getargspec
_split_list = pydoc._split_list
_is_bound_method = pydoc._is_bound_method
npml = skip_object = False


# -------------------------------------------- Markdown documentation generator


class MarkdownRepr(Repr):
    """Class for safely making a Markdown representation of a Python object."""

    def __init__(self):
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    def repr1(self, x, level):
        if hasattr(type(x), "__name__"):
            methodname = "repr_" + "_".join(type(x).__name__.split())
            if hasattr(self, methodname):
                return getattr(self, methodname)(x, level)
        return cram(stripid(repr(x)), self.maxother)

    def repr_string(self, x, level):
        test = cram(x, self.maxstring)
        testrepr = repr(test)
        if "\\" in test and "\\" not in replace(testrepr, r"\\", ""):
            # Backslashes are only literal in the string and are never
            # needed to make any special characters, so show a raw string.
            return "r" + testrepr[0] + test + testrepr[0]
        return testrepr

    repr_str = repr_string

    def repr_instance(self, x, level):
        try:
            return cram(stripid(repr(x)), self.maxstring)
        except Exception:
            return "[%s instance]" % x.__class__.__name__

    def escape(self, text):
        if text[:1] == " ":
            return text
        return replace(
            text,
            "&",
            "&amp;",
            "<",
            "&lt;",
            ">",
            "&gt;",
            "_",
            "\\_",
            "*",
            "\\*",
            "#",
            "\\#",
        )


class MarkdownDoc(Doc):
    """Formatter class for Markdown documentation."""

    # ------------------------------------------- text formatting utilities

    _repr_instance = MarkdownRepr()
    repr = _repr_instance.repr
    escape = _repr_instance.escape

    def bold(self, text):
        """Format a string in bold by overstriking."""
        return "**" + text.replace("*", "\\*") + "**"

    def indent(self, text, prefix="    "):
        """Indent text by prepending a given prefix to each line."""
        if not text:
            return ""
        lines = [(prefix + line).rstrip() for line in text.split("\n")]
        return "\n".join(lines)

    def _heading(self, text, h="#"):
        return h + " " + text.strip().replace("\n", "<br />")

    def section(self, title, contents, pfx="###"):
        """Format a section with a given heading."""
        # clean_contents = self.indent(contents).rstrip()
        clean_contents = contents.rstrip()
        if clean_contents:
            return self._heading(title, pfx) + "\n\n" + clean_contents
        return self._heading(title, pfx)

    def bigsection(
        self,
        title,
        cls,
        contents,
        width=None,
        prelude=None,
        marginalia=None,
        gap=None,
    ):
        """Format a section with a big heading."""
        c = []
        if prelude and prelude.strip():
            c.append(prelude.rstrip())
        if contents and contents.strip():
            c.append(contents.rstrip())
        return self.section(title, "\n\n".join(c), pfx="##")

    def document(self, object, name=None, *args):
        """Generate documentation for an object."""
        args = (object, name) + args
        # 'try' clause is to attempt to handle the possibility that inspect
        # identifies something in a way that pydoc itself has issues handling;
        # think 'super' and how it is a descriptor (which raises the exception
        # by lacking a __name__ attribute) and an instance.
        try:
            if inspect.ismodule(object):
                return self.docmodule(*args)
            if inspect.isclass(object):
                return self.docclass(*args)
            if inspect.isroutine(object):
                return self.docroutine(*args)
        except AttributeError:
            raise
        if inspect.isdatadescriptor(object):
            return self.docdata(*args)
        return self.docother(*args)

    def filelink(self, url, path=None):
        """Make a link to source file."""
        # strip out root path if link is to file names
        if url.startswith(sys.path[0]):
            url = url[len(sys.path[0]) :].lstrip("/")

        if path is None:
            path = url

        if path.startswith(sys.path[0]):
            path = path[len(sys.path[0]) :].lstrip("/")

        return f"[{path}]({url})"

    def namelink(self, name, *dicts):
        """Make a link for an identifier, given name-to-URL mappings."""
        for dict in dicts:
            if name in dict:
                link = dict[name]
                return self.filelink(link, name)
        return name

    def markup(self, text, escape=None, funcs={}, classes={}, methods={}):
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape = escape or self.escape
        results = []
        here = 0
        pattern = re.compile(
            r"\b((http|https|ftp)://\S+[\w/]|"
            r"RFC[- ]?(\d+)|"
            r"PEP[- ]?(\d+)|"
            r"(self\.)?(\w+))"
        )
        indented = 0
        while match := pattern.search(text, here):
            start, end = match.span()
            results.append(escape(text[here:start]))
            if "\n" in results[-1]:
                indented = "\n    " in results[-1]

            if indented:
                results.append(text[start:end])
                here = end
                continue

            all, scheme, rfc, pep, selfdot, name = match.groups()
            if scheme:
                url = escape(all).replace('"', "&quot;")
                results.append(self.filelink(url, url))
            elif rfc:
                url = "https://www.rfc-editor.org/rfc/rfc%d.txt" % int(rfc)
                results.append(self.filelink(url, escape(all)))
            elif pep:
                url = "https://peps.python.org/pep-%04d/" % int(pep)
                results.append(self.filelink(url, escape(all)))
            elif selfdot:
                # Create a link for methods like 'self.method(...)'
                # and use <strong> for attributes like 'self.attr'
                if text[end : end + 1] == "(":
                    results.append("self. " + self.namelink(name, methods))
                else:
                    results.append(f"self.{name}")
            elif text[end : end + 1] == "(":
                results.append(self.namelink(name, methods, funcs, classes))
            else:
                results.append(self.namelink(name, classes))
            here = end
        if indented:
            results.append(text[here:])
        else:
            results.append(escape(text[here:]))

        lines = "".join(results).split("\n")
        for i, l in enumerate(lines):
            if l[:1] == "[" and l.split()[0][-2:] == "()":
                lines[i] = l.rstrip() + "  "
        return "\n".join(lines)

    def preformat(self, text):
        """Format literal preformatted text."""
        lines = text.expandtabs().split("\n")
        for i, l in enumerate(lines):
            ld = len(l) - len(l.lstrip())
            if ld:
                lines[i] = ld * " " + l.lstrip().replace("  ", "&nbsp; ")
            else:
                lines[i] = self.escape(l).replace("  ", "&nbsp; ")

        return "\n".join(lines)

        return f"""```
{text}
```"""

    def item_list(self, list, format, prefix=""):
        if len(list) < 2:
            return format(list[0])

        suf1 = "" if prefix else "  "

        li = len(list) - 1

        return "\n".join(
            prefix + format(item) + ("" if i == li else suf1)
            for i, item in enumerate(list)
        )

    # multicolumn is ugly, lists are less ugly
    multicolumn = item_list

    def classlink(self, object, modname):
        """Make a link for a class."""
        name, module = object.__name__, sys.modules.get(object.__module__)
        cn = classname(object, modname)
        if hasattr(module, name) and getattr(module, name) is object:
            # link = dict[name]
            mn = module.__name__
            return self.filelink(f"{mn}.md#{name}", cn)
        return cn

    def parentlink(self, object, modname):
        """Make a link for the enclosing class or module."""
        link = None
        name, module = object.__name__, sys.modules.get(object.__module__)
        if hasattr(module, name) and getattr(module, name) is object:
            if "." in object.__qualname__:
                name = object.__qualname__.rpartition(".")[0]
                if object.__module__ != modname:
                    link = "%s.md#%s" % (module.__name__, name)
                else:
                    link = "#%s" % name
            else:
                if object.__module__ != modname:
                    link = "%s.md" % module.__name__
        if link:
            name = parentname(object, modname)
            return self.filelink(link, name)
        else:
            return parentname(object, modname)

    def modulelink(self, object):
        name = object.__name__
        """Make a link for a module."""

        if "lib/python" in object.__file__:
            link = f"https://docs.python.org/3/library/{name}.html"
        else:
            link = name + ".md"

        return self.filelink(link, name)

    def modpkglink(self, modpkginfo):
        """Make a link for a module or package to display in an index."""
        name, path, ispackage, shadowed = modpkginfo
        if shadowed:
            return self.grey(name)
        if path:
            url = "%s.%s.md" % (path, name)
        else:
            url = "%s.md" % name
        if ispackage:
            text = "*%s* (package)" % name
        else:
            text = name
        return self.filelink(url, text)

    # ---------------------------------------------- type-specific routines

    def formattree(self, tree, modname, parent=None, prefix=""):
        """Produce Markdown for a class tree as given by inspect.getclasstree()."""
        result = []
        skipped = 0
        for entry in tree:
            if isinstance(entry, tuple):
                c, bases = entry
                if c is builtins.object and skip_object:
                    skipped = 1
                    continue
                skipped = 0
                cl = self.classlink(c, modname)
                parent = ""
                if skip_object:
                    bases = tuple(
                        b for b in bases if not (b is builtins.object)
                    )
                if bases and bases != (parent,):
                    parents = []
                    for base in bases:
                        parents.append(self.classlink(base, modname))
                    parent = " (" + ", ".join(parents) + ")"
                result.append(prefix + "* " + cl + parent)
            elif isinstance(entry, list):
                pp = "" if skipped else "  "
                result.extend(
                    pp + prefix + row
                    for row in self.formattree(entry, modname, c)
                    .rstrip()
                    .split("\n")
                )
        return "\n".join(result)

    def docmodule(self, object, name=None, mod=None, *ignored):
        """Produce Markdown documentation for a module object."""
        name = object.__name__  # ignore the passed-in name
        try:
            all = object.__all__
        except AttributeError:
            all = None

        if npml:
            linkedname = name
        else:
            parts = name.split(".")
            links = []
            for i in range(len(parts) - 1):
                links.append(self.filelink(".".join(parts[: i + 1]), parts[i]))
            linkedname = ".".join(links + parts[-1:])
        head = self.section(linkedname, "", pfx="##")
        try:
            path = inspect.getabsfile(object)
            url = urllib.parse.quote(path)
            filelink = self.filelink(url, path)
        except TypeError:
            filelink = "(built-in)"
        info = []
        if hasattr(object, "__version__"):
            version = str(object.__version__)
            if version[:11] == "$" + "Revision: " and version[-1:] == "$":
                version = version[11:-1].strip()
            info.append("version %s" % self.escape(version))
        if hasattr(object, "__date__"):
            info.append(self.escape(str(object.__date__)))
        if info:
            head = head + " (%s)" % ", ".join(info)
        docloc = self.getdocloc(object)
        if docloc is not None:
            docloc = self.filelink(docloc, "Module Reference")
        else:
            docloc = ""
        result = [head.rstrip() + " " + filelink + "\n\n" + docloc]
        result[-1] = result[-1].rstrip()

        modules = []
        builtin_modules = []
        for m in inspect.getmembers(object, inspect.ismodule):
            if "lib/python" in m[1].__file__:
                builtin_modules.append(m)
            else:
                modules.append(m)

        classes, cdict = [], {}
        for key, value in inspect.getmembers(object, inspect.isclass):
            # if __all__ exists, believe it.  Otherwise use old heuristic.
            if (
                all is not None
                or (inspect.getmodule(value) or object) is object
            ):
                if visiblename(key, all, object):
                    classes.append((key, value))
                    cdict[key] = cdict[value] = "#" + key
        for key, value in classes:
            for base in value.__bases__:
                key, modname = base.__name__, base.__module__
                module = sys.modules.get(modname)
                if modname != name and module and hasattr(module, key):
                    if getattr(module, key) is base:
                        if key not in cdict:
                            cdict[key] = cdict[base] = modname + ".md#" + key
        funcs, fdict = [], {}
        imported_funcs = {}
        for key, value in inspect.getmembers(object, inspect.isroutine):
            # if __all__ exists, believe it.  Otherwise use a heuristic.
            if (
                all is not None
                or inspect.isbuiltin(value)
                or (inspect.getmodule(value) or object) is object
            ):
                if visiblename(key, all, object):
                    funcs.append((key, value))
                    fdict[key] = "#-" + key
                    if inspect.isfunction(value):
                        fdict[value] = fdict[key]
            elif "lib/python" not in inspect.getmodule(value).__file__:
                mn = inspect.getmodule(value).__name__
                if mn not in imported_funcs:
                    imported_funcs[mn] = []
                link = mn + ".md#-" + key
                imported_funcs[mn].append(self.filelink(link, f"{key}()"))
        data = []
        for key, value in inspect.getmembers(object, isdata):
            if visiblename(key, all, object):
                data.append((key, value))

        doc = self.markup(getdoc(object), self.preformat, fdict, cdict)
        if doc:
            result.append(doc)

        if hasattr(object, "__path__"):
            modpkgs = []
            for importer, modname, ispkg in pkgutil.iter_modules(
                object.__path__
            ):
                modpkgs.append((modname, name, ispkg, 0))
            modpkgs.sort()
            contents = self.multicolumn(modpkgs, self.modpkglink)
            result.append(
                self.bigsection("Package Contents", "pkg-content", contents)
            )
        else:
            if modules:
                contents = self.multicolumn(
                    modules, lambda t: self.modulelink(t[1])
                )
                result.append(
                    self.bigsection("Imported modules", "pkg-content", contents)
                )

            if builtin_modules:
                contents = self.multicolumn(
                    builtin_modules, lambda t: self.modulelink(t[1])
                )
                result.append(
                    self.bigsection("Builtin modules", "pkg-content", contents)
                )

        if classes:
            classlist = [value for (key, value) in classes]
            contents = [
                self.formattree(
                    inspect.getclasstree(classlist, 1), name
                ).rstrip()
            ]
            for key, value in classes:
                contents.append(
                    self.document(value, key, name, fdict, cdict).rstrip()
                )
            result.append(
                self.bigsection(
                    "Classes defined here", "index", "\n\n".join(contents)
                )
            )
        if funcs:
            contents = []
            for key, value in funcs:
                contents.append(
                    self.document(value, key, name, fdict, cdict).rstrip()
                )
            result.append(
                self.bigsection(
                    "Functions defined here", "functions", "\n\n".join(contents)
                )
            )

        if imported_funcs:
            ifc = []
            for src, functions in sorted(imported_funcs.items()):
                fname = src.replace(".", "/") + ".py"
                ifc.append(
                    "From "
                    + self.bold(self.filelink(src + ".md", src))
                    + " "
                    + self.filelink(fname)
                )
                for fcn in sorted(functions):
                    ifc.append("* " + fcn)
                ifc.append("")

            if ifc:
                ifc.pop()

            result.append(
                self.bigsection(
                    "Imported functions", "functions", "\n".join(ifc)
                )
            )
        if data:
            contents = []
            for key, value in data:
                contents.append(self.document(value, key).rstrip())
            result.append(
                self.bigsection("Data", "data", "\n\n".join(contents))
            )

        if hasattr(object, "__author__"):
            contents = self.markup(str(object.__author__), self.preformat)
            result.append(
                self.bigsection("Author", "author", contents).rstrip()
            )

        if hasattr(object, "__credits__"):
            contents = self.markup(str(object.__credits__), self.preformat)
            result.append(
                self.bigsection("Credits", "credits", contents).rstrip()
            )

        return "\n\n".join(result)

    def hr(self):
        return "---\n"

    def docclass(self, object, name=None, mod=None, *ignored):
        """Produce Markdown documentation for a given class object."""
        realname = object.__name__
        name = name or realname
        bases = object.__bases__

        def makename(c, m=object.__module__):
            return classname(c, m)

        if name == realname:
            title = (
                f'### class <a name="{realname}">'
                + self.escape(realname)
                + "</a>"
            )
        else:
            title = self.bold(name) + " = class " + realname
        if bases:
            parents = map(makename, bases)
            title = title + "(%s)" % ", ".join(parents)

        contents = []
        push = contents.append

        argspec = _getargspec(object)
        if argspec and argspec != "()":
            push(name + argspec + "\n")

        doc = getdoc(object)
        if doc:
            push(doc + "\n")

        # List the mro, if non-trivial.
        mro = deque(inspect.getmro(object))
        if len(mro) > 2:
            push("Method resolution order:")
            for base in mro:
                push("    " + makename(base))
            push("")

        # List the built-in subclasses, if any:
        subclasses = sorted(
            (
                str(cls.__name__)
                for cls in type.__subclasses__(object)
                if (
                    not cls.__name__.startswith("_")
                    and getattr(cls, "__module__", "") == "builtins"
                )
            ),
            key=str.lower,
        )
        no_of_subclasses = len(subclasses)
        MAX_SUBCLASSES_TO_DISPLAY = 4
        if subclasses:
            push("Built-in subclasses:")
            for subclassname in subclasses[:MAX_SUBCLASSES_TO_DISPLAY]:
                push("    " + subclassname)
            if no_of_subclasses > MAX_SUBCLASSES_TO_DISPLAY:
                push(
                    "    ... and "
                    + str(no_of_subclasses - MAX_SUBCLASSES_TO_DISPLAY)
                    + " other subclasses"
                )
            push("")

        # Cute little class to pump out a horizontal rule between sections.
        class HorizontalRule:
            def __init__(self):
                self.needone = bool(doc)

            def maybe(sel):
                if sel.needone:
                    push(self.hr())
                sel.needone = 1

        hr = HorizontalRule()

        def spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    try:
                        value = getattr(object, name)
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(self.docdata(value, name, mod))
                    else:
                        push(self.document(value, name, mod, object, homecls))
                push("")
            return attrs

        def spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    push(self.indent(self.docdata(value, name, mod)))
                push("")
            return attrs

        def spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    doc = getdoc(value)
                    try:
                        obj = getattr(object, name)
                    except AttributeError:
                        obj = homecls.__dict__[name]
                    push(
                        self.indent(
                            self.docother(obj, name, mod, maxlen=70, doc=doc)
                        )
                    )
                push("")
            return attrs

        attrs = [
            (name, kind, cls, value)
            for name, kind, cls, value in classify_class_attrs(object)
            if visiblename(name, obj=object)
        ]

        while attrs:
            if mro:
                thisclass = mro.popleft()
            else:
                thisclass = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] is thisclass)

            if object is not builtins.object and thisclass is builtins.object:
                attrs = inherited
                continue
            elif thisclass is object:
                tag = "defined here"
            else:
                tag = "inherited from %s" % classname(
                    thisclass, object.__module__
                )

            sort_attributes(attrs, object)

            # Pump out the attrs, segregated by kind.
            attrs = spill(
                "Methods %s:\n" % tag, attrs, lambda t: t[1] == "method"
            )
            attrs = spill(
                "Class methods %s:\n" % tag,
                attrs,
                lambda t: t[1] == "class method",
            )
            attrs = spill(
                "Static methods %s:\n" % tag,
                attrs,
                lambda t: t[1] == "static method",
            )
            attrs = spilldescriptors(
                "Readonly properties %s:\n" % tag,
                attrs,
                lambda t: t[1] == "readonly property",
            )
            attrs = spilldescriptors(
                "Data descriptors %s:\n" % tag,
                attrs,
                lambda t: t[1] == "data descriptor",
            )
            attrs = spilldata(
                "Data and other attributes %s:\n" % tag,
                attrs,
                lambda t: t[1] == "data",
            )

            assert attrs == []
            attrs = inherited

        contents = "\n".join(contents)
        if not contents:
            return title

        return title + "\n\n" + contents.rstrip()

    def formatvalue(self, object):
        """Format an argument default value as text."""
        return "=" + self.repr(object)

    def docroutine(
        self,
        object,
        name=None,
        mod=None,
        funcs={},
        classes={},
        methods={},
        cl=None,
        homecls=None,
    ):
        """Produce Markdown documentation for a function or method object."""
        realname = object.__name__
        name = name or realname
        if homecls is None:
            homecls = cl
        anchor = ("" if cl is None else cl.__name__) + "-" + name
        note = ""
        skipdocs = False
        imfunc = None
        if _is_bound_method(object):
            imself = object.__self__
            if imself is cl:
                imfunc = getattr(object, "__func__", None)
            elif inspect.isclass(imself):
                note = " class method of %s" % self.classlink(imself, mod)
            else:
                note = " method of %s instance" % self.classlink(
                    imself.__class__, mod
                )
        elif inspect.ismethoddescriptor(object) or inspect.ismethodwrapper(
            object
        ):
            try:
                objclass = object.__objclass__
            except AttributeError:
                pass
            else:
                if cl is None:
                    note = " unbound %s method" % self.classlink(objclass, mod)
                elif objclass is not homecls:
                    note = " from " + self.classlink(objclass, mod)
        else:
            imfunc = object
        if (
            inspect.isfunction(imfunc)
            and homecls is not None
            and (
                imfunc.__module__ != homecls.__module__
                or imfunc.__qualname__ != homecls.__qualname__ + "." + realname
            )
        ):
            pname = self.parentlink(imfunc, mod)
            if pname:
                note = " from %s" % pname

        if inspect.iscoroutinefunction(object) or inspect.isasyncgenfunction(
            object
        ):
            asyncqualifier = "async "
        else:
            asyncqualifier = ""

        if name == realname:
            title = '<a name="%s">%s</a>' % (anchor, realname)
        else:
            if (
                cl is not None
                and inspect.getattr_static(cl, realname, []) is object
            ):
                reallink = self.file_link(
                    "#" + cl.__name__ + "-" + realname, realname
                )
                skipdocs = True
                if note.startswith(" from "):
                    note = ""
            else:
                reallink = realname
            title = '<a name="%s">%s</a> = %s' % (anchor, name, reallink)
        argspec = None
        if inspect.isroutine(object):
            argspec = _getargspec(object)
            if argspec and realname == "<lambda>":
                title = "*%s* *lambda* " % name.replace("*", "\\*")
                # XXX lambda's won't usually have func_annotations['return']
                # since the syntax doesn't support but it is possible.
                # So removing parentheses isn't truly safe.
                if not object.__annotations__:
                    argspec = argspec[1:-1]  # remove parentheses
        if not argspec:
            argspec = "(...)"

        decl = asyncqualifier + title + self.escape(argspec) + (note or "")

        if skipdocs:
            return decl

        doc = self.markup(
            getdoc(object), self.preformat, funcs, classes, methods
        )
        return self.section(decl, doc)

    def grey(self, text):
        return text

    def docdata(self, object, name=None, mod=None, cl=None, *ignored):
        """Produce Markdown documentation for a data descriptor."""
        results = []
        push = results.append

        if name:
            push(name)
            push("\n")
        doc = getdoc(object) or ""
        if doc:
            push(self.indent(doc))
        return "".join(results)

    docproperty = docdata

    def docother(
        self,
        object,
        name=None,
        mod=None,
        parent=None,
        *ignored,
        maxlen=None,
        doc=None,
    ):
        """Produce Markdown documentation for a data object."""
        repr = self.repr(object)
        if maxlen:
            line = (name and name + " = " or "") + repr
            chop = maxlen - len(line)
            if chop < 0:
                repr = repr[:chop] + "..."
        line = (name and name + " = " or "") + repr
        if not doc:
            doc = getdoc(object)
        if doc:
            line += "\n\n" + self.indent(str(doc))
        return line

    def page(self, title, body):
        """Produce a Markdown page"""
        return self._heading(title).rstrip() + "\n\n" + body.rstrip() + "\n"


md = MarkdownDoc()


def writedoc(thing, forceload=0):
    """Write Markdown documentation to a file in the current directory."""
    object, name = resolve(thing, forceload)
    page = md.page(describe(object), md.document(object, name))
    with open(name + ".md", "w", encoding="utf-8") as file:
        file.write(page)


def writedocs(dir, pkgpath="", done=None):
    """Write out Markdown documentation for all modules in a directory tree."""
    if done is None:
        done = {}
    for importer, modname, ispkg in pkgutil.walk_packages([dir], pkgpath):
        writedoc(modname)
    return


_tf = None
_tc = None


def spewtar(filename: str):
    """
    Add `filename` to the stdout tarfile
    """
    import tarfile

    global _tf, _tc
    if not _tf:
        _tf = io.BytesIO()
        _tc = tarfile.open(mode="w", fileobj=_tf)

    _tc.add(filename)


def finishtar():
    """
    Dump the stdout tarfile contents to stdout.
    """
    global _tf, _tc
    if _tf:
        sys.stdout.buffer.write(_tf.getvalue())
    _tf = _tc = None


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tar",
        default=False,
        action="store_true",
        help="When provided, add all newly generated dotted.module.md to stdout tar.",
    )
    parser.add_argument(
        "--no-module-parent",
        default=False,
        action="store_true",
        help="If provided, do not include a link to the module's parent.",
    )
    parser.add_argument(
        "--skip-object",
        default=False,
        action="store_true",
        help="If provided, will skip listing builtins.object as a parent class.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--stdin",
        default=False,
        action="store_true",
        help="If provided, will read stdin as though it was an uncompressed tar file of .py files to run pydoc_md on. Implies --tar .",
    )
    group.add_argument(
        "path",
        nargs="*",
        help="Any dotted.module name will be imported and processed into a dotted.module.md . "
        "File paths ending with '.py', [./]*dotted/module.py -> dotted.module, and processed into dotted.module.md . "
        "File paths ending with '.md' will be added to stdout as part of a tar file. "
        "WARNING: md.py files should use the 'path' format including the .py for proper processing.",
    )
    return parser.parse_args(args)


def main(parsed=None):
    # some binary strings don't round trip through utf-8, and we found some!
    sys.stdin.reconfigure(encoding="latin-1")
    global npml, skip_object
    if not parsed:
        parsed = parse_args()
    args = parsed
    if args.no_module_parent:
        npml = True
    if args.skip_object:
        skip_object = True

    path = None
    if args.stdin:
        args.tar = True
        # read tar input
        path = tempfile.TemporaryDirectory()
        sys.path.insert(0, path.name)
        a = io.BytesIO()
        a.write(sys.stdin.read().encode("latin-1"))
        a.seek(0)
        files = tarfile.open(mode="r", fileobj=a)
        files.extractall(path.name)
        for dp, dn, fn in os.walk(path.name):
            for f in fn:
                if f.endswith(".py"):
                    dest = os.path.join(dp, f)
                    args.path.append(dest[len(path.name) :].lstrip("/"))

        args.path.sort()
        args.path.reverse()

    for arg in args.path:
        # spew markdown files as tar
        if args.path[0].endswith(".md"):
            spewtar(arg)
            continue

        # handle .py pathnames
        if arg.endswith(".py"):
            # [./]*path/name.py -> path.name
            arg = arg.lstrip("./").replace("/", ".")[:-3]

        # generate the docs
        writedoc(arg)
        if args.tar:
            spewtar(arg + ".md")

    finishtar()


if __name__ == "__main__":
    main()
