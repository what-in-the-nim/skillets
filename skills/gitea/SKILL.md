---
name: gitea
description: >-
  Use for Gitea work through the `tea` CLI: repository and login discovery, pull
  requests, issues, comments, labels, releases, branches, actions, and authenticated
  Gitea API requests. Trigger when a task mentions Gitea, `tea`, a Gitea pull request
  or issue, or a Gitea review or comment.
allowed-tools: Bash, Read, Grep, Glob
---

# Gitea

Use `tea` as the Gitea client. Run it from the target repository so it can derive the
repository and matching login from the Git remote.

## Resolve the target

1. Run from the repository root. If the target is unclear, inspect it with `git remote -v`.
2. Let `tea` discover the login from the current remote.
3. If discovery fails, inspect configured servers with `tea logins list`.
4. When more than one remote or login is possible, make the target explicit with the
   command's supported `--remote`, `--login`, or `--repo` option.
5. Use `tea whoami` when the acting identity affects the result.

Treat the repository, Gitea server, login, and requested entity as resolved only when
the command target is unambiguous. If no login is configured, report that the user must
complete `tea logins add`; keep credentials in tea's configuration rather than in
command arguments or repository files.

## Choose the operation

- Prefer the entity command (`tea pulls`, `tea issues`, `tea comments`, `tea labels`,
  `tea releases`, and so on) over a raw HTTP client.
- Use `--output yaml` or `--output json` when another step must consume the result.
- Use `tea --help` or `<entity> --help` when syntax or available fields is uncertain.
- Use `tea api` only when the entity command does not expose the needed operation. It
  still uses tea's authenticated context; quote endpoints containing `?` or `&`.

## Read before changing

Read the current entity before a state-changing operation. For example:

```bash
N=743
tea pulls "$N" --fields index,title,state,author,url,body,mergeable,base,head --output yaml
tea issues "$N" --fields index,title,state,author,url,body,labels --output yaml
tea comments "$N" --output yaml
```

Use the full diff field for pull-request review context:

```bash
tea pulls "$N" --fields diff --output simple
```

## Change safely

Treat create, edit, close, reopen, approve, reject, merge, delete, comment, and
non-`GET` `tea api` calls as mutations.

- Confirm the resolved target and requested change before mutating it.
- Keep long bodies in a scratch Markdown or JSON file, then pass the file contents to
  tea; never put credentials in those files.
- Run exactly the requested mutation and inspect its output or re-read the entity.
- Report the actual result, including any server error, instead of inferring success
  from an empty response.

For non-interactive pull-request verdicts, use the dedicated commands:

```bash
BODY_FILE=/tmp/gitea-body.md
tea pulls approve "$N" "$(cat "$BODY_FILE")"
tea pulls reject "$N" "$(cat "$BODY_FILE")"
```

Use `tea comments add` for a normal issue or pull-request comment. `tea pulls review`
is interactive; use it only when the surrounding workflow provides that interaction.

## Completion

A Gitea operation is complete when tea ran against an unambiguous target, the requested
read or mutation returned, and the result was checked and reported.
