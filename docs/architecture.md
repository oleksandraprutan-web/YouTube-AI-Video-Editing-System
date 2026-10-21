# Architecture

These supplied diagrams illustrate the workflow used to develop the system. Counts and thresholds shown are specific to that example, not benchmarks or quality guarantees.

## Recording and take reports

![Teleprompter layers](media/teleprompter-layers.png)

![How one take becomes a report](media/take-report-architecture.png)

## Across-take planning

![Recording plan architecture](media/edit-plan-architecture.png)

The teleprompter's draft combines attempts against script lines. Its latest-attempt heuristic is a starting point; the editing agent and human must compare complete readings. `edit-plan.json` is not the final source-linked editor timeline.

![Example attempts selected into a cut](media/tries-to-cut.png)

## Editing and QA

![Agent cut layers](media/agent-cut-layers.png)

The diagram's “no merges” means keeping editable source mapping, not requiring redundant boundaries between contiguous source intervals. The public assembler writes a candidate, and diagnostic QA writes separate reports. A human chooses when to load it into Eyeline Edit. Automatic edge detection is fallible; audition the final words and joins.

For the precise distinction between recording plans, edit plans, final transcripts and board timing, see [formats](formats.md).
