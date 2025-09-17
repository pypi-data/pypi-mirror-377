# pydzn
*Pronounced:* **[paɪ dɪˈzaɪn]** — “**pie design**” (aka **py-design**)

Design and develop complex websites all in python. Build web components, rendered on the server-side and served up in any python backend web server (flask, django...).

More than just a view layer, pydzn serves as a framework that introduces python developers to front end development with an intuitive approach for layout design, component development and styling.

## Who is pydzn for
- Python fluent programmers who find designing and developing nice looking websites a frustrating task
- Students learning python who also want to learn how to build websites
- Backend developers and data scientists who want to build AI-embedded web applications
- Front-end developers who value simplicity while maintaining full control over their runtime
- Professional front-end developers who want to avoid react abstraction bloat and javascript's async chaos

## Why pydzn
Creating and serving a webpage is technically easy for most developers. Designing and developing a nice looking website is much more difficult. pydzn offers a framework for breaking up the task of front-end design and development, logically, into layout creation, component creation with the injection of those components into that layout. Where a layout is a grid in a 2-dimensional space containing named regions of which you style and inject components into. A layout is a class which can have an arbitrary number of regions. A region is a placement in a grid layout for which another layout OR component can be injected.

## Introduction

### Layouts
A website is a design in a 2-dimensional space, therefore, a design divides that 2-dimensional space into regions. We've made this easy to do in pydzn with the `layout_builder`. With a little practice you'll start seeing other websites as "grid layouts" and you'll find it easy to recreate them in pydzn. Let's start by creating a generic page layout.

```python
@app.route("/tutorial")
def tutorial():
    from pydzn.grid_builder import layout_builder

    APPBAR_HEIGHT=100
    HERO_HEIGHT=200
    BODY_HEIGHT=400
    FOOTER_HEIGHT=200
    DEBUG=True

    GenericPageLayout = (
        layout_builder()
        .fill_height("100%", property="height")
        .columns(c0="1fr") # for the base layout we only need one column because each row will be it's own region
        .rows(r0=APPBAR_HEIGHT, r1=HERO_HEIGHT, r2=BODY_HEIGHT, r3=FOOTER_HEIGHT) # each row is a section of the web page in this case
        .region("appbar", row="r0", col="c0") # the appbar belongs in row 0 and column 0
        .region("hero", row="r1", col="c0")
        .region("body", row="r2", col="c0")
        .region("footer", row="r3", col="c0")
        .build(name="GenericPageLayout")
    )

    body = GenericPageLayout(debug=DEBUG).render() # set debug=True in order view the layout lines and region names for easier development
    return render_template("index.html", body=body)
```

<p align="center">
  <img src="docs/simple_website_layout_start.png" alt="mobile" width="640">
</p>

The layout we've created is a common layout containing an appbar, hero, body and footer. Let's now inject the appbar layout into the appbar region.

```python
...
    AppBarLayout = (
        layout_builder()
        .fill_height("100%", property="height")
        .columns(c0="1fr", c1="3fr", c2="1fr", c3="1fr", c4="1fr") # we'll divide the app bar into 5 columns and we'll make c1 a spacer
        .rows(r0=APPBAR_HEIGHT) # we've previously set the appbar height so we'll use it
        .region("brand", row="r0", col="c0")
        .region("spacer0", row="r0", col="c1")
        .region("about", row="r0", col="c2")
        .region("contact", row="r0", col="c3")
        .region("services", row="r0", col="c4")
        .build(name="AppBarLayout")
    )

    body = GenericPageLayout(debug=DEBUG).render(
        appbar=AppBarLayout(debug=DEBUG).render()  # appbar, like hero, body and footer are variables in the render function's signature
    )
    return render_template("index.html", body=body)
```

<p align="center">
  <img src="docs/simple_website_layout_appbar.png" alt="mobile" width="640">
</p>

Next let's add some of pydzn pre-made components into the appbar.

```python
...
    from pydzn.components import Text, NavItem

    body = GenericPageLayout(debug=DEBUG).render(
        appbar=AppBarLayout(debug=DEBUG).render(
            brand=Text(
                text="Acme Widgets", 
                dzn="text-[#272727]").render(), # let's give the text a color using pydzn semantic classes
            about=NavItem(
                children=Text(
                    text="About Us", dzn="text-[#272727]").render()
                    ).no_underline().center().as_link("/#").render(),
            contact=NavItem(
                children=Text(text="Contact Us", dzn="text-[#272727]").render()
                ).no_underline().center().as_link("/#").render(),
            services=NavItem(
                children=Text(text="Services", dzn="text-[#272727]").render()
                ).no_underline().center().as_link("/#").render()
        )
    )
    return render_template("index.html", body=body)
```
<p align="center">
  <img src="docs/simple_website_layout_appbar_components.png" alt="mobile" width="640">
</p>

We inject complex components (NavItem composed of Text) into the region slots inside `AppBarLayout`, however, I don't like how they look inside their respective regions. pydzn provides a dzn controls on layouts in order to define the layout within each region. Let's center each of these components in their respective region.

```python
...
    from pydzn.components import Text, NavItem

    body = GenericPageLayout(
        debug=DEBUG,).render(
        appbar=AppBarLayout(
            debug=DEBUG,
            region_dzn={
            "brand": "flex items-center justify-center", # pydzn provides fine control on individual region styles using the dzn semantic classes
            "about": "flex items-center justify-center",
            "contact": "flex items-center justify-center",
            "services": "flex items-center justify-center"
        }).render(
            brand=Text(text="Acme Widgets", dzn="text-[#272727]").render(), # let's give the text a color using pydzn semantic classes
            about=NavItem(
                children=Text(
                    text="About Us", dzn="text-[#272727]").render()).no_underline().center().as_link("/#").render(),
            contact=NavItem(
                children=Text(
                    text="Contact Us", dzn="text-[#272727]").render()).no_underline().center().as_link("/#").render(),
            services=NavItem(
                children=Text(text="Services", dzn="text-[#272727]").render()).no_underline().center().as_link("/#").render()
        )
    )
    return render_template("index.html", body=body)
```

<p align="center">
  <img src="docs/simple_website_layout_appbar_components_centered.png" alt="mobile" width="640">
</p>

Pydzn offers utilities for serving responsive websites and leverages htmx to provide complex functionality within your web pages. To be continued...

## Examples
- For examples see: [pydzn-website](https://github.com/anthonyrka/pydzn-website)

## References
- See [PyPI](https://pypi.org/project/pydzn/)
