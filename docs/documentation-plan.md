# Documentation plan

Eleven Trainer serves Quest owners who want repeatable ball-machine practice and contributors who maintain the local tool. A newcomer needs a complete first experience, including developer mode; an experienced player needs short task guides. The command reference and design rationale remain separate from both.

| Document / location | Type | Reader need and audience | Must cover | Depends on | Wave | Volatility and rationale |
|---|---|---|---|---|---|---|
| First training, `tutorials/first-training.md` | Tutorial | New Quest owner: teach me the whole workflow | Developer registration, verification, developer mode, drivers, ADB, export, select, repeat, validate, install, observe | CLI reference | 1 | High: Meta UI and game file access change; a guided success gives the reader confidence |
| Create a session, `how-to/create-session.md` | How-to | Player: practice one shot or a sequence at my pace | Single-shot output, ordered selections, 10/2 phases, interval, saved files | First training | 1 | Low: follows CLI; focused on completing a practice task |
| Connect over Wi-Fi, `how-to/wifi.md` | How-to | Player: remove the cable | USB bootstrap, IP, connection, authorization, reconnection, disable TCP mode | First training | 2 | High: firmware and network behavior; separate from the USB learning path |
| Recover and troubleshoot, `how-to/recover.md` | How-to | Player: recover after a failed command | Local vs ADB errors, missing settings, backups, restore | CLI reference | 1 | Medium: error paths change; gives direct recovery actions |
| CLI, `reference/cli.md` | Reference | User/contributor: look up syntax | Commands, defaults, exit codes, file locations | None | 1 | Tracks releases; mirrors argparse |
| Settings and compatibility, `reference/settings.md` | Reference | Contributor: inspect supported data | JSON contract, supported fields, ordering, limits, evidence boundaries | None | 2 | High: unofficial game format; facts must be separated from assumptions |
| Why this tool, `explanation/rationale.md` | Explanation | Player/contributor: understand design choices | Repetition progression, preserved trajectories, local architecture, restart tradeoffs, AI boundaries | None | 1 | Stable: records motivations and alternatives |
| Licensing and sources, `explanation/sources.md` | Explanation | Contributor: understand why drill packs are excluded | Own code vs third-party data, attribution, provenance | None | 2 | Medium: permissions may change; prevents confusing free download with open licensing |

## Navigation and delivery

`README.md` is the project front door. `docs/index.md` routes by reader need into `tutorials/`, `how-to/`, `reference/`, and `explanation/`. An Estonian start page links to the same maintained reference rather than duplicating every command.

Distribution: one deliberate end-to-end tutorial in English and Estonian, three task guides, two references, two explanations. Wave 1 supports a complete USB workflow; wave 2 adds wireless operation and contributor detail. Both waves are in the initial release scope.

Open verification items: confirm current Meta UI against official documentation; distinguish historical device observations from testing of this new package; never imply that file readback proves ball trajectories or loop timing. The new package needs a later hardware acceptance test. No additional audience or product-scope decision is required before writing.
