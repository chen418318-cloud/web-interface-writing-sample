# Reset a Filtered Interface Without Leaving Its Results Behind

Original personal teaching sample prepared with OpenAI Codex assistance. Six invented records; no client data or commercial-project claim. [Runnable source](index.html) and [executed browser-check summary](verification.md) accompany this article. This is a sample for editorial review, not a commissioned article.

A reset button can appear to work while leaving a page in the wrong state. The search field clears, a category menu returns to its first option, and the result panel still says that nothing matches. A user has performed the right action, but the interface gives them no way to trust it.

This tutorial builds a small, framework-free product filter and repairs that inconsistency. The useful lesson is how to keep derived interface state connected to native form controls. You can open the accompanying index.html directly or serve it with a static HTTP server. Nothing is installed, fetched or submitted.

## 1. Define an observable outcome

Our page contains six invented products in two categories, Desk and Travel. It has a search input, a category select, a reset button, product cards, a result count and an empty state. The form defaults are an empty search and All categories.

Write the expected behavior before changing the event handlers. Searching for Cobalt should show two products. Combining that search with Desk should show only Cobalt Notebook. Resetting either that one-result state or a zero-result state should restore six products, both control defaults and the normal result panel.

This makes the bug measurable. A button changing appearance is not enough: inspect the controls and the content they determine.

## 2. Keep the controls native

The filter is an ordinary form. Labels are connected to the input and select by their for and id attributes. The reset control is a button with type="reset". Its label is Reset filters, which tells the user what will change.

The result count is a separate status element:

```html
<p id="result-count" role="status"
   aria-live="polite" aria-atomic="true"></p>
```

This expresses the intention that changes should be announced without moving focus. It does not prove that every screen reader will announce the text as intended. A real accessibility review still needs the relevant assistive technology and user flows.

Each product is an article with a heading and two data attributes: data-name and data-category. These are local, invented records, not a live catalog. Using real semantic elements also makes the page's visible state easier to inspect.

## 3. Calculate all derived output in one place

The renderResults function reads the current controls every time it runs. It trims the query, makes it lowercase and evaluates the name and category conditions together. A product is visible only when both conditions match.

```js
function renderResults() {
  const term = query.value.trim().toLowerCase();
  let matches = 0;
  for (const product of products) {
    const nameMatches = product.dataset.name.includes(term);
    const categoryMatches = category.value === 'all' ||
      category.value === product.dataset.category;
    product.hidden = !(nameMatches && categoryMatches);
    if (!product.hidden) matches += 1;
  }
  resultCount.textContent = `${matches} of ${products.length} products`;
  empty.hidden = matches !== 0;
}
```

The result count and the empty message come from the same pass as the product visibility. If those updates lived in separate handlers, one could easily be forgotten during the next change.

The page calls this function on input and change events, then once on initial load. Its submit listener prevents an Enter key submission from navigating away; filtering here is a local interaction rather than a search request to a server.

## 4. Reproduce the incomplete reset

Open index.html?mode=before. Enter zzzz into Search products. There are no matches, so the cards disappear and the empty message appears. Press Reset filters.

The native controls return to their defaults, but the derived content stays at zero. That is the deliberately broken version: it has input and change handlers but no reset handler that refreshes the results.

Resetting a form restores the form's control defaults. It does not know how this particular page derives product visibility, counts or messages. Those outputs belong to the application.

## 5. Refresh after the reset action

In the corrected version, add this listener:

```js
form.addEventListener('reset', () => {
  requestAnimationFrame(renderResults);
});
```

The reset event is part of the reset operation rather than a promise that your application has already finished rebuilding its derived UI. Scheduling a frame callback lets the browser complete the native reset action before this page reads the controls again and updates its visible content.

MDN describes requestAnimationFrame as a request for a callback before an upcoming repaint. It is a one-shot callback. Here one call is sufficient because there is one redraw to perform; this is not an animation loop or a fixed-duration timeout.

Open index.html without the before parameter and repeat the zero-result sequence. The count returns to six, the cards return and the empty message disappears. Repeat from the combined Cobalt and Desk filter as well: the same listener restores both controls and all six results.

## 6. Check the behavior that the article promises

These checks were executed through the available Codex in-app browser. The accompanying verification.md summarizes the recorded control values, result counts and empty-state observations for each step.

```text
  Initial page                    empty / All categories   6 results
  Search Cobalt                   Cobalt / All categories  2 results
  Add Desk category               Cobalt / Desk            1 result
  Reset the combined filter       empty / All categories   6 results
  Choose Travel                   empty / Travel           3 results
  Search zzzz while in Travel     zzzz / Travel            0 results
  Reset the zero-result state     empty / All categories   6 results
```

All seven corrected-version checks passed. The deliberately broken version reproduced its expected reset failure. The retained local browser evidence also includes before-and-after screenshots; this public summary does not claim any additional browser coverage.

## Boundaries for a larger application

The example uses a tiny synchronous data set. A server-backed search also needs to cancel or disregard stale responses; a frame callback cannot guarantee that network work has finished. If defaults are preselected rather than blank, reset should restore those defaults, so the renderer must continue reading the actual controls.

Frame callbacks can pause in hidden tabs. This example schedules a visible UI refresh; it should not be used as a hidden-tab background processing guarantee. Production filters may also need debouncing, URL state, pagination and data-volume checks.

The supplied evidence covers one available browser surface. It is not a claim of Firefox, Safari, mobile-device or screen-reader testing. Use the same explicit acceptance checks on the environments your project actually supports.

## References checked for this sample

MDN, HTMLFormElement: reset event:
https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reset_event

MDN, Window: requestAnimationFrame() method:
https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame

The accompanying source file is the complete runnable example. The code blocks in the article are excerpts from that source, not a second implementation.
