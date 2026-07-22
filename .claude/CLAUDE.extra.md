# Extended Project Context

Consumer-optional overflow file. Holds project-specific context that does not
belong in the root CLAUDE.md; the goal is to keep root CLAUDE.md lean (under
about 200 lines). The template ships this file unwired so its placeholder
content never enters session context.

To activate it when your project needs the overflow, add these two lines to
the end of CLAUDE.md:

## Extended Context
See @.claude/CLAUDE.extra.md for API references, workarounds, and environment notes.

## API References
- [Add API docs URLs relevant to this project]

## External Dependencies
- [Document third-party services, their endpoints, auth methods]

## Known Workarounds
- [Temporary hacks that exist in the codebase and why]

## Environment-Specific Notes
- [Dev vs staging vs prod differences Claude should know about]

## Historical Decisions
- [Why we chose X over Y; context that prevents Claude from suggesting Y]
