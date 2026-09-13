/** Compile and validate in an offline browser, leaving only static report content. */
(async () => {
  try {
    const forbidden = document.querySelector('iframe, object, embed, base, link, img, video, audio, source');
    if (forbidden || document.querySelectorAll('script').length !== 2) {
      throw new Error('Report fragments must be static HTML without scripts or external assets');
    }
    for (const element of document.querySelectorAll('*')) {
      if ([...element.attributes].some(a => /^on/i.test(a.name) || /javascript:/i.test(a.value))) {
        throw new Error('Active report content is unsupported');
      }
    }
    mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default',
      deterministicIds: true, deterministicIDSeed: 'quick-refactor' });
    const diagrams = [...document.querySelectorAll('pre.mermaid')];
    for (const [index, diagram] of diagrams.entries()) {
      const { svg } = await mermaid.render(`diagram-${index}`, diagram.textContent);
      diagram.parentElement.innerHTML = svg;
    }
    // Namespace every SVG-local ID, including Mermaid's shared sequence markers.
    for (const [index, svg] of [...document.querySelectorAll('svg')].entries()) {
      const ids = new Map();
      for (const node of [svg, ...svg.querySelectorAll('[id]')]) {
        if (!node.id) continue;
        if (ids.has(node.id)) throw new Error(`Duplicate ID within SVG: ${node.id}`);
        ids.set(node.id, `svg-${index}-${node.id}`);
      }
      /** Rewrite ID references without interpreting color literals as selectors. */
      const references = value => value.replace(/url\(["']?#([^\s)'" ]+)["']?\)/g,
        (whole, id) => ids.has(id) ? `url(#${ids.get(id)})` : whole);
      for (const node of [svg, ...svg.querySelectorAll('*')]) {
        for (const attribute of [...node.attributes]) {
          let value = references(attribute.value);
          if (attribute.name === 'id') value = ids.get(value);
          if (['href', 'xlink:href'].includes(attribute.name) && value.startsWith('#')) {
            value = `#${ids.get(value.slice(1)) || value.slice(1)}`;
          }
          if (['aria-labelledby', 'aria-describedby'].includes(attribute.name)) {
            value = value.split(/\s+/).map(id => ids.get(id) || id).join(' ');
          }
          node.setAttribute(attribute.name, value);
        }
      }
      for (const style of svg.querySelectorAll('style')) {
        let css = references(style.textContent);
        for (const [oldId, newId] of ids) {
          const escaped = oldId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          css = css.replace(new RegExp(`#${escaped}(?![\\w-])(?=[^{}]*\\{)`, 'g'), `#${newId}`);
        }
        style.textContent = css;
      }
    }
    document.querySelectorAll('script').forEach(script => script.remove());
    const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
    if (new Set(ids).size !== ids.length) throw new Error('Duplicate report/SVG IDs');
    for (const node of document.querySelectorAll('[href], [xlink\\:href], [aria-labelledby], [aria-describedby]')) {
      for (const name of ['href', 'xlink:href', 'aria-labelledby', 'aria-describedby']) {
        const value = node.getAttribute(name);
        if (!value) continue;
        const refs = name.startsWith('aria-') ? value.split(/\s+/) : value.startsWith('#') ? [value.slice(1)] : [];
        for (const ref of refs) if (!ids.includes(ref)) throw new Error(`Broken reference: ${ref}`);
      }
    }
    for (const match of document.documentElement.outerHTML.matchAll(/url\(["']?#([^\s)'" ]+)["']?\)/g)) {
      if (!ids.includes(match[1])) throw new Error(`Broken SVG reference: ${match[1]}`);
    }
    if (document.querySelectorAll('.diagram > svg').length !== diagrams.length) {
      throw new Error('Missing compiled diagram');
    }
    const sections = [...document.querySelectorAll('main > section')];
    const links = [...document.querySelectorAll('nav a')];
    if (links.length !== sections.length || sections.some((s, i) => links[i].getAttribute('href') !== `#${s.id}`)) {
      throw new Error('Navigation does not match report sections');
    }
    document.querySelector('meta[http-equiv="Content-Security-Policy"]').content =
      "default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:";
    document.body.dataset.renderStatus = 'complete';
  } catch (error) {
    document.body.dataset.renderError = error.message;
  }
})();
