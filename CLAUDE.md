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


Init prompt:
Help me implement a feature for Explaino (@app/README.md). This will be the place where everything gets explained to the user.
Right now I have two major features planned.
The first one is explaining a term, a sentence, or basically any piece of text.
The key idea is that the input text can be explored, not like ChatGPT where you only continue chatting in a linear way. In this app, explanations can branch. A user can open sub‑explanations, go deeper into a topic, go back, and then continue exploring another subtopic.
Think of it like a depth‑first search (DFS) through knowledge.
The second feature is teaching a topic to a user. The app can generate a course based on a topic. A course contains lessons, each lesson contains study notes and quizzes to test whether the user understands the topic.
There will be three modes for generating courses:
For kids, the course will include more images and less text.
For normal users, it will be balanced between text, images, and maybe videos.
For advanced users or experts, it can use more resources to generate the course, possibly including deep research APIs.
