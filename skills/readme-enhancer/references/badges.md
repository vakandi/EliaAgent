# Shields.io Badge Reference

## Format

```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}?logo={LOGO}&logoColor={LOGO_COLOR}
```

## Common Colors

| Color | Hex |
|-------|-----|
| Blue | `blue` |
| Green | `green` |
| Orange | `orange` |
| Red | `red` |
| Yellow | `yellow` |
| Purple | `purple` |
| Black | `black` |
| Gray | `lightgrey` |

## Language Badges

```markdown
<!-- Python -->
<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">

<!-- TypeScript -->
<img src="https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?logo=typescript&logoColor=white" alt="TypeScript">

<!-- Node.js -->
<img src="https://img.shields.io/badge/Node.js-18%2B-339933?logo=node.js&logoColor=white" alt="Node.js">
```

## Framework Badges

```markdown
<!-- React -->
<img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" alt="React">

<!-- Next.js -->
<img src="https://img.shields.io/badge/Next.js-14-000000?logo=next.js" alt="Next.js">

<!-- FastAPI -->
<img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">

<!-- Tailwind -->
<img src="https://img.shields.io/badge/Tailwind-3.4-06B6D4?logo=tailwind-css&logoColor=white" alt="Tailwind">
```

## Package Manager Badges

```markdown
<!-- npm -->
<a href="https://npmjs.com/package/PACKAGE_NAME">
  <img src="https://img.shields.io/npm/v/PACKAGE_NAME.svg?logo=npm" alt="npm">
</a>

<!-- PyPI -->
<a href="https://pypi.org/project/PACKAGE_NAME/">
  <img src="https://img.shields.io/pypi/v/PACKAGE_NAME.svg?logo=pypi&logoColor=white" alt="PyPI">
</a>
```

## Platform Badges

```markdown
<!-- GitHub -->
<a href="https://github.com/USER/REPO">
  <img src="https://img.shields.io/github/stars/USER/REPO?logo=github" alt="GitHub Stars">
</a>

<!-- License -->
<a href="LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
</a>

<!-- CI -->
<a href="https://github.com/USER/REPO/actions">
  <img src="https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml?logo=github" alt="CI">
</a>
```

## Custom Message Format

```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}
```

- URL-encode spaces as `%20`
- URL-encode `+` as `%2B`
- URL-encode `%` as `%25`

## Logo List

Browse available logos: https://simpleicons.org/

Common ones: `python`, `javascript`, `typescript`, `node.js`, `react`, `next.js`, `vue`, `docker`, `kubernetes`, `aws`, `github`, `gitlab`, `npm`, `pypi`, `fastapi`, `flask`, `django`, `postgresql`, `mongodb`, `redis`, `tailwind-css`, `figma`
