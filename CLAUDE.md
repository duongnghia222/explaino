# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Explaino is a React + TypeScript web application. The frontend lives in the `web/` directory and uses Vite as the build tool.

## Commands

All commands run from the `web/` directory:

```bash
cd web
npm run dev      # Start dev server with HMR
npm run build    # Type-check (tsc -b) then build for production
npm run lint     # ESLint
npm run preview  # Preview production build
```

## Tech Stack

- React 19, TypeScript 5.9, Vite 7
- @vitejs/plugin-react (Babel-based)
- ESLint with typescript-eslint and react-hooks/react-refresh plugins
