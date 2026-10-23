# Executed browser checks

The sample was exercised on 23 October 2026 through the Codex in-app browser using six invented product records. OpenAI Codex assisted with preparation; observations came from the rendered interface.

| Step | Query | Category | Expected and observed visible records | Result |
| --- | --- | --- | --- | --- |
| Initial page | blank | All categories | 6 | Pass |
| Search | Cobalt | All categories | 2 | Pass |
| Combine category | Cobalt | Desk | 1, Cobalt Notebook | Pass |
| Reset combined filter | blank | All categories | 6 | Pass |
| Category only | blank | Travel | 3 | Pass |
| Zero matches | zzzz | Travel | 0, empty-state text shown | Pass |
| Reset zero-result state | blank | All categories | 6, empty-state text hidden | Pass |

The deliberately broken mode, index.html?mode=before, reproduced its intended failure: after searching zzzz and pressing reset, controls returned to their defaults while the visible results remained at zero. The corrected mode restored both control and result state.

To inspect the demo, download the repository and open index.html in a browser, or use a standard static local server. The GitHub source viewer does not execute HTML. No dependencies or external requests are needed.

Coverage is limited to the available in-app browser. These observations do not establish mobile hardware, Firefox, Safari, screen-reader, production or large-data compatibility. The status markup expresses an accessibility intention; screen-reader announcements were not tested. No customer data or commercial client work is represented.
