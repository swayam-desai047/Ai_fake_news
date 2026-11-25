import type { jsPDF as JsPDF } from 'jspdf';
import type { Article } from './types';
import { DIMENSIONS, DISCLAIMER, METHOD_NOTE } from './dimensions';
import { sectionLabel } from './sections';
import { dateTime } from './format';

/**
 * Client-side A4 intelligence report (handover §6 step 4 layout) for any article in the edition.
 * Only recorded values are printed: missing scores or confidence are stated as missing.
 */

const INK: [number, number, number] = [23, 23, 23];
const GREY: [number, number, number] = [98, 98, 98];
const RULE: [number, number, number] = [216, 214, 208];
const RED: [number, number, number] = [198, 45, 45];

/** The PDF standard fonts only cover Windows-1252. */
function pdfSafe(text: string): string {
    return text
        .replace(/₹\s*/g, 'Rs ')
        .replace(/[‐-‒]/g, '-')
        .replace(/[^\x00-\xFF–—‘’“”•…€]/g, '');
}

export async function generateIntelligencePdf(article: Article): Promise<void> {
    const { jsPDF } = await import('jspdf');
    const doc: JsPDF = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const W = doc.internal.pageSize.getWidth();
    const H = doc.internal.pageSize.getHeight();
    const M = 16;
    const CW = W - M * 2;
    let y = M;

    const ensure = (needed: number) => {
        if (y + needed > H - 22) {
            doc.addPage();
            y = M;
        }
    };
    const rule = (weight = 0.2, color = RULE) => {
        doc.setDrawColor(...color);
        doc.setLineWidth(weight);
        doc.line(M, y, W - M, y);
    };
    const label = (text: string, color = GREY) => {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7);
        doc.setTextColor(...color);
        doc.text(pdfSafe(text.toUpperCase()), M, y);
    };
    const para = (text: string, size = 10, font: 'times' | 'helvetica' = 'times', style = 'normal', width = CW, x = M) => {
        doc.setFont(font, style);
        doc.setFontSize(size);
        doc.setTextColor(...INK);
        const lines = doc.splitTextToSize(pdfSafe(text), width) as string[];
        const lh = size * 0.42;
        for (const line of lines) {
            ensure(lh);
            doc.text(line, x, y);
            y += lh;
        }
    };

    // Nameplate
    doc.setFont('times', 'bold');
    doc.setFontSize(24);
    doc.setTextColor(...INK);
    doc.text('The Daily Signal', W / 2, y + 6, { align: 'center' });
    y += 11;
    doc.setFont('times', 'italic');
    doc.setFontSize(9);
    doc.setTextColor(...GREY);
    doc.text('Article Intelligence Report', W / 2, y, { align: 'center' });
    y += 4;
    rule(0.6, INK);
    y += 1;
    rule(0.2, INK);
    y += 5;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.text(pdfSafe(`Generated ${dateTime(new Date().toISOString())}`), M, y);
    doc.text(pdfSafe(article.analysisMethod === 'model' ? 'Backend pipeline analysis (models + rules)' : 'Rule-based analysis of feed excerpt'), W - M, y, { align: 'right' });
    y += 9;

    // Article
    label(`${sectionLabel(article.section)} · ${article.publisher}`, RED);
    y += 6;
    para(article.title, 17, 'times', 'bold');
    y += 2;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(...GREY);
    doc.text(pdfSafe(`Published ${dateTime(article.publishedAt)}`), M, y);
    y += 4;
    if (article.sourceUrl) {
        const url = doc.splitTextToSize(article.sourceUrl, CW) as string[];
        doc.setTextColor(...INK);
        doc.textWithLink(url[0], M, y, { url: article.sourceUrl });
        y += 4;
    }
    y += 3;

    // Excerpt and summary (both printed when both exist; neither is invented)
    const blocks: [string, string][] = [];
    if (article.excerpt) blocks.push(['Publisher excerpt (RSS)', article.excerpt]);
    if (article.summary && article.summaryKind) blocks.push([article.summaryKind === 'ai' ? 'AI summary' : 'Extractive summary', article.summary]);
    if (blocks.length === 0) blocks.push(['Publisher excerpt (RSS)', 'The feed supplied a headline only.']);
    for (const [heading, text] of blocks) {
        rule();
        y += 5;
        label(heading);
        y += 5;
        para(text.replace(/\n\n/g, ' '), 10.5);
        y += 3;
    }

    // Credibility
    ensure(30);
    rule(0.4, INK);
    y += 5;
    label('Credibility indicators');
    y += 7;
    const c = article.credibility;
    const cols = [
        ['Risk label', c.label === 'Unavailable' ? 'Not assessed' : c.label],
        ['Risk score (0-1)', c.score !== null ? c.score.toFixed(2) : 'Not computed'],
        ['Classifier fake score', typeof c.modelFakeProbability === 'number' ? c.modelFakeProbability.toFixed(2) : 'Not available'],
        ['Classifier confidence', c.confidence !== null ? `${Math.round(c.confidence * 100)}%` : 'Not reported'],
        ['Verification', c.needsVerification ? 'Needs verification' : 'Not flagged'],
    ];
    cols.forEach(([k, v], i) => {
        const x = M + (CW / 5) * i;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(6.5);
        doc.setTextColor(...GREY);
        doc.text(pdfSafe(k.toUpperCase()), x, y);
        doc.setFont('times', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(...INK);
        doc.text(pdfSafe(v), x, y + 5.5);
    });
    y += 11;
    if (c.reasoning) {
        para(c.reasoning, 9, 'times', 'italic');
    }
    y += 4;

    // Dimensions
    ensure(20);
    rule(0.4, INK);
    y += 5;
    label('Eight-dimension content analysis');
    y += 6;
    if (!article.dimensions) {
        para('No dimension scores are recorded for this article.', 10, 'times', 'italic');
    } else {
        const dims = article.dimensions;
        for (const d of DIMENSIONS) {
            const explanation = dims.explanations[d.key] ?? 'No explanation recorded.';
            const lines = doc.splitTextToSize(pdfSafe(explanation), CW - 70) as string[];
            const rowH = Math.max(10, lines.length * 3.6 + 5);
            ensure(rowH);
            doc.setFont('times', 'bold');
            doc.setFontSize(10);
            doc.setTextColor(...INK);
            doc.text(pdfSafe(d.label), M, y);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(6.5);
            doc.setTextColor(...GREY);
            doc.text(pdfSafe(`0 ${d.low} - 100 ${d.high}`), M, y + 3.6);
            // score bar (empty when the dimension could not be scored)
            const score = dims[d.key];
            doc.setDrawColor(...RULE);
            doc.setLineWidth(0.2);
            doc.rect(M + 48, y - 2.4, 14, 2.2);
            if (score !== null) {
                doc.setFillColor(...INK);
                doc.rect(M + 48, y - 2.4, (14 * score) / 100, 2.2, 'F');
            }
            doc.setFont('times', score !== null ? 'bold' : 'italic');
            doc.setFontSize(score !== null ? 10 : 8);
            doc.setTextColor(...INK);
            doc.text(score !== null ? String(score) : 'n/a', M + 64, y);
            doc.setFont('times', 'normal');
            doc.setFontSize(8.5);
            doc.text(lines, M + 70, y);
            y += rowH;
            rule();
            y += 4;
        }
    }

    // Method & disclaimer
    ensure(30);
    y += 2;
    label('Method');
    y += 5;
    para(METHOD_NOTE[article.analysisMethod], 8.5, 'times', 'normal');
    if (c.status || c.modelVersion) {
        y += 1;
        para(`Analysis status: ${c.status ?? 'not recorded'}${c.modelVersion ? ` · ${c.modelVersion}` : ''}`, 8, 'helvetica', 'normal');
    }
    y += 3;
    rule(0.4, INK);
    y += 5;
    para(DISCLAIMER, 8.5, 'times', 'italic');

    const pages = doc.getNumberOfPages();
    for (let p = 1; p <= pages; p++) {
        doc.setPage(p);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7);
        doc.setTextColor(...GREY);
        doc.text('The Daily Signal · MIT-WPU M.Sc Computer Science, Group 17', M, H - 10);
        doc.text(`Page ${p} of ${pages}`, W - M, H - 10, { align: 'right' });
    }

    const slug = article.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 50).replace(/-$/, '');
    doc.save(`daily-signal-report-${slug}.pdf`);
}
