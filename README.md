# rentalincostarica.com — Home / Portfolio

GitHub user-site repo for [rentalincostarica.com](https://rentalincostarica.com/).

Hosts the bilingual landing page that lists rental properties. Each property is
its own repo deployed as a project site under the same custom domain:

| Path on rentalincostarica.com         | Source repo                |
|----------------------------------------|----------------------------|
| `/`                                    | this repo (`luiskarlos.github.io`) |
| `/jaco-live-local/`                    | [`jaco-live-local`](https://github.com/luiskarlos/jaco-live-local) |
| `/<future-property>/`                  | future repo               |

## Setup

1. **Repo**: this folder must be pushed as `https://github.com/luiskarlos/luiskarlos.github.io` (the exact name `luiskarlos.github.io` is what GitHub Pages recognizes as a user site).
2. **Pages source**: Settings → Pages → Source = `Deploy from a branch`, Branch = `main`, Folder = `/docs`.
3. **Custom domain**: Settings → Pages → Custom domain = `rentalincostarica.com` (already in `docs/CNAME`).
4. **DNS** (GoDaddy):
   - 4 `A` records `@` → `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`
   - 1 `CNAME` `www` → `luiskarlos.github.io`
5. Once DNS resolves, enable **Enforce HTTPS** in Pages settings.

## Adding a new property

1. Create or use an existing repo for the property (e.g. `tamarindo-villa-3`).
2. Enable Pages on that repo (`Branch=main`, `Folder=/docs`).
3. **Do not** set a custom domain on the project repo — it inherits `rentalincostarica.com` automatically because this user site has it.
4. Add a new `<a class="prop">` card in `docs/index.html` and `docs/en/index.html` here, linking to `/repo-name/`.

## Local preview

```bash
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```
