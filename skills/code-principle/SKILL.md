---
name: code-principle
description: Apply these surgical code principle whenever writing, modifying, or refactoring code. Preserve manual formatting, require docstrings, prefer reusable composition, limit inline comments, and communicate tersely.
---

# Code Principle

Write the smallest coherent change. Apply every rule below to code you create or modify.

## Rules

1. **Preserve manual formatting.** Leave formatting to the user. Do not run formatters or formatting commands, and avoid incidental formatting-only edits.
2. **Document every new code unit.** Every new class, function, and method gets a docstring. Start with a concise one-line summary and stop there when it is sufficient. When contracts, side effects, errors, or non-obvious decisions need more explanation, expand it into full NumPy style using only relevant sections.
3. **Design through composition.** Before implementing a module or class, identify separable, general mechanisms. Prefer composing reusable components behind the domain-facing API when they have an independent responsibility, contract, or testing value. Keep behavior local when extraction would be speculative.
4. **Keep inline comments scarce.** Each inline comment is one concise line and explains why, not what. Use at most two inline comments within a function or method. Move deeper explanation into a method docstring or a nearby `README.md`.
5. **Stay surgical.** Begin with the smallest correct patch that fits the current design. Refactor only when the required change is growing, and limit the refactor to what makes that change coherent.
6. **Communicate tersely.** Use compact engineering prose in reasoning and handoff. Sentence fragments are acceptable when meaning stays unambiguous; preserve decisions, risks, and verification evidence.

## Completion Check

Before finishing, verify:

- no formatter or formatting command was run;
- every new module, class, function, and method has an appropriately sized docstring;
- each new module or class was checked for useful component boundaries without speculative extraction;
- every function or method has at most two one-line inline comments;
- the diff contains only the smallest coherent implementation or its necessary refactor; and
- the explanation is terse without hiding decisions, risks, or verification results.
