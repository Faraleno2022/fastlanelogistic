/**
 * Recherche dynamique + recalcul automatique des totaux + pagination client-side.
 *
 * Utilisation :
 *   <input type="text" data-table-search="#tblCarburant" placeholder="Rechercher...">
 *   <span data-search-count="#tblCarburant"><b class="cnt-visible"></b>/<b class="cnt-total"></b></span>
 *
 *   <table id="tblCarburant" data-searchable data-page-size="50">
 *     <thead>
 *       <tr>
 *         <th>Date</th>
 *         <th class="text-end" data-sum="sum" data-format="int">Montant</th>
 *       </tr>
 *     </thead>
 *     <tbody> ... </tbody>
 *   </table>
 *
 * Attributs :
 *   data-searchable      → active recherche + tri + pagination
 *   data-page-size="N"   → taille de page (défaut 50, 0 = pas de pagination)
 *   data-sum="sum|avg|count|min|max" sur <th>
 *   data-format="int|dec1|dec2|pct"  sur <th>
 *   data-sortable        → colonne triable (actif d'office si data-sum)
 *
 * Totaux : calculés sur TOUTES les lignes filtrées (pas seulement la page courante)
 * Tri : cliquer sur un <th> pour trier asc/desc, la pagination se met à jour.
 * Pagination : nav Bootstrap insérée juste après le tableau, se cache s'il n'y a qu'une page.
 */
(function () {
  'use strict';
  const FR_LOCALE = 'fr-FR';

  function parseNumber(txt) {
    if (txt == null) return NaN;
    let s = String(txt).trim();
    if (!s || s === '—' || s === '-') return NaN;
    s = s.replace(/\u00a0/g, ' ').replace(/\s+/g, '');
    if (s.indexOf('.') !== -1 && s.indexOf(',') !== -1) {
      s = s.replace(/\./g, '').replace(',', '.');
    } else if ((s.match(/,/g) || []).length === 1 && s.indexOf('.') === -1) {
      s = s.replace(',', '.');
    } else {
      s = s.replace(/,/g, '');
    }
    s = s.replace(/[^0-9.\-]/g, '');
    const n = parseFloat(s);
    return isNaN(n) ? NaN : n;
  }

  function formatNumber(n, fmt) {
    if (n == null || isNaN(n)) return '—';
    if (fmt === 'pct') return n.toFixed(1) + ' %';
    const opts = { maximumFractionDigits: 0, minimumFractionDigits: 0 };
    if (fmt === 'dec1') { opts.maximumFractionDigits = 1; opts.minimumFractionDigits = 1; }
    else if (fmt === 'dec2') { opts.maximumFractionDigits = 2; opts.minimumFractionDigits = 2; }
    return n.toLocaleString(FR_LOCALE, opts);
  }

  // ---------------- Init ----------------
  function initTable(table) {
    if (!table.id) { console.warn('[table_search] Table sans id', table); return; }
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    const pageSize = parseInt(table.dataset.pageSize || '50', 10);
    const ths = Array.from(table.querySelectorAll('thead th'));
    const sumCols = [];
    ths.forEach((th, idx) => {
      const mode = th.dataset.sum;
      if (mode) {
        sumCols.push({
          index: idx, mode: mode,
          format: th.dataset.format || 'int',
        });
      }
    });

    let tfoot = table.querySelector('tfoot');
    if (!tfoot) {
      tfoot = document.createElement('tfoot');
      tfoot.className = 'table-secondary fw-bold';
      table.appendChild(tfoot);
    }

    // Conteneur pagination (après la balise .table-responsive englobante si présente)
    let paginationEl = document.querySelector(`[data-pagination-for="#${table.id}"]`);
    if (!paginationEl) {
      paginationEl = document.createElement('nav');
      paginationEl.className = 'mt-2 d-flex justify-content-between align-items-center flex-wrap gap-2';
      paginationEl.setAttribute('data-pagination-for', '#' + table.id);
      // Insérer juste après le parent .table-responsive, ou après la table
      const anchor = table.closest('.table-responsive') || table;
      anchor.parentNode.insertBefore(paginationEl, anchor.nextSibling);
    }

    const searchInput = document.querySelector(`[data-table-search="#${table.id}"]`);
    const countEl     = document.querySelector(`[data-search-count="#${table.id}"]`);

    let currentPage = 1;

    function isEmptyStateRow(row) {
      return row.cells.length === 1 && row.cells[0].colSpan > 1;
    }

    function recompute() {
      const allRows = Array.from(tbody.querySelectorAll('tr'));
      const dataRows = allRows.filter(r => !isEmptyStateRow(r));
      const emptyRows = allRows.filter(isEmptyStateRow);

      const q = (searchInput && searchInput.value || '').trim().toLowerCase();
      const filtered = dataRows.filter(r => !q || r.textContent.toLowerCase().includes(q));

      // Totaux sur lignes filtrées (toutes pages confondues)
      const acc = {};
      sumCols.forEach(c => { acc[c.index] = { sum: 0, count: 0, min: Infinity, max: -Infinity }; });
      filtered.forEach(r => {
        sumCols.forEach(c => {
          const cell = r.cells[c.index];
          if (!cell) return;
          const v = parseNumber(cell.textContent);
          if (!isNaN(v)) {
            acc[c.index].sum += v;
            acc[c.index].count++;
            if (v < acc[c.index].min) acc[c.index].min = v;
            if (v > acc[c.index].max) acc[c.index].max = v;
          }
        });
      });

      // Pagination
      const total = filtered.length;
      const nbPages = pageSize > 0 ? Math.max(1, Math.ceil(total / pageSize)) : 1;
      if (currentPage > nbPages) currentPage = nbPages;
      if (currentPage < 1) currentPage = 1;

      const start = pageSize > 0 ? (currentPage - 1) * pageSize : 0;
      const end   = pageSize > 0 ? Math.min(start + pageSize, total) : total;
      const visibleInPage = filtered.slice(start, end);
      const visibleSet = new Set(visibleInPage);

      // Appliquer l'affichage
      dataRows.forEach(r => {
        r.style.display = visibleSet.has(r) ? '' : 'none';
      });
      // Empty row : visible si AUCUNE donnée, sinon cachée
      emptyRows.forEach(r => { r.style.display = dataRows.length === 0 ? '' : 'none'; });

      // Reconstruire tfoot
      tfoot.innerHTML = '';
      const tr = document.createElement('tr');
      ths.forEach((th, i) => {
        const td = document.createElement('td');
        const sc = sumCols.find(c => c.index === i);
        if (sc) {
          const a = acc[i];
          let val;
          switch (sc.mode) {
            case 'avg':   val = a.count ? a.sum / a.count : 0; break;
            case 'count': val = a.count; break;
            case 'min':   val = a.count ? a.min : 0; break;
            case 'max':   val = a.count ? a.max : 0; break;
            default:      val = a.sum;
          }
          td.textContent = formatNumber(val, sc.format);
          td.className = 'text-end fw-bold';
          td.title = `${sc.mode.toUpperCase()} sur ${a.count} ligne(s) filtrée(s)`;
        } else if (i === 0) {
          td.innerHTML = `<span class="text-muted">TOTAUX <span class="badge bg-primary">${total}</span> filtré(s)</span>`;
        }
        tr.appendChild(td);
      });
      tfoot.appendChild(tr);

      // Compteur
      if (countEl) {
        const vis = countEl.querySelector('.cnt-visible');
        const tot = countEl.querySelector('.cnt-total');
        if (vis) vis.textContent = total;
        if (tot) tot.textContent = dataRows.length;
        countEl.classList.toggle('text-warning', q && total < dataRows.length);
      }

      // Pagination UI
      renderPagination(total, nbPages, start, end);
    }

    function renderPagination(total, nbPages, start, end) {
      paginationEl.innerHTML = '';
      if (total === 0 || pageSize === 0) return;

      // Info gauche
      const info = document.createElement('small');
      info.className = 'text-muted';
      info.innerHTML = `<i class="bi bi-file-earmark-text"></i> Lignes ${start + 1}–${end} sur <b>${total}</b>${nbPages > 1 ? ` · page ${currentPage}/${nbPages}` : ''}`;
      paginationEl.appendChild(info);

      if (nbPages <= 1) return;

      // UL pagination
      const ul = document.createElement('ul');
      ul.className = 'pagination pagination-sm mb-0';

      function addItem(label, page, opts) {
        opts = opts || {};
        const li = document.createElement('li');
        li.className = 'page-item' + (opts.disabled ? ' disabled' : '') + (opts.active ? ' active' : '');
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.innerHTML = label;
        if (!opts.disabled && !opts.active) {
          a.addEventListener('click', function (e) {
            e.preventDefault();
            currentPage = page;
            recompute();
            // Scroll doux vers le haut du tableau
            const anchor = table.closest('.table-responsive') || table;
            anchor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          });
        } else {
          a.addEventListener('click', function (e) { e.preventDefault(); });
        }
        li.appendChild(a);
        ul.appendChild(li);
      }

      addItem('«', 1,               { disabled: currentPage === 1 });
      addItem('‹', currentPage - 1, { disabled: currentPage === 1 });

      // Fenêtre de pages (1 2 … N-1 N avec cluster central)
      const window_ = 2;
      const pages = new Set([1, nbPages, currentPage]);
      for (let i = currentPage - window_; i <= currentPage + window_; i++) {
        if (i >= 1 && i <= nbPages) pages.add(i);
      }
      const sorted = Array.from(pages).sort((a, b) => a - b);
      let prev = 0;
      sorted.forEach(p => {
        if (p - prev > 1) addItem('…', p, { disabled: true });
        addItem(String(p), p, { active: p === currentPage });
        prev = p;
      });

      addItem('›', currentPage + 1, { disabled: currentPage === nbPages });
      addItem('»', nbPages,         { disabled: currentPage === nbPages });

      paginationEl.appendChild(ul);
    }

    // Listeners
    if (searchInput) {
      searchInput.addEventListener('input', function () {
        currentPage = 1;   // reset page quand filtre change
        recompute();
      });
      searchInput.addEventListener('search', function () { currentPage = 1; recompute(); });
    }

    // Tri par colonne
    ths.forEach((th, idx) => {
      if (th.dataset.sortable !== undefined || th.dataset.sum) {
        th.style.cursor = 'pointer';
        th.style.userSelect = 'none';
        if (!th.querySelector('.sort-icon')) {
          const icon = document.createElement('span');
          icon.className = 'sort-icon text-muted ms-1';
          icon.innerHTML = '⇅';
          th.appendChild(icon);
        }
        let asc = true;
        th.addEventListener('click', () => {
          const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => !isEmptyStateRow(r));
          rows.sort((a, b) => {
            const va = a.cells[idx]?.textContent.trim() || '';
            const vb = b.cells[idx]?.textContent.trim() || '';
            const na = parseNumber(va);
            const nb = parseNumber(vb);
            if (!isNaN(na) && !isNaN(nb)) return asc ? na - nb : nb - na;
            return asc ? va.localeCompare(vb, FR_LOCALE) : vb.localeCompare(va, FR_LOCALE);
          });
          rows.forEach(r => tbody.appendChild(r));
          asc = !asc;
          table.querySelectorAll('.sort-icon').forEach(el => el.innerHTML = '⇅');
          const icon = th.querySelector('.sort-icon');
          if (icon) icon.innerHTML = asc ? '▼' : '▲';
          currentPage = 1;
          recompute();
        });
      }
    });

    recompute();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('table[data-searchable]').forEach(initTable);
  });
})();
