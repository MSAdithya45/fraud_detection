import { cn } from "@/utils/cn";

// Render inline **bold** segments.
function renderInline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold text-slate-900">
        {part.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

/**
 * Lightweight Markdown renderer for the LLM explanation.
 * Supports headings (#, ##, ###), bullet lists (-, *), bold, and paragraphs.
 */
export default function MarkdownMessage({ content, className }) {
  const lines = String(content || "").split("\n");
  const blocks = [];
  let list = null;

  const flushList = () => {
    if (list) {
      blocks.push({ type: "ul", items: list });
      list = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^#{1,6}\s/.test(line)) {
      flushList();
      blocks.push({
        type: "h",
        level: line.match(/^#+/)[0].length,
        text: line.replace(/^#+\s/, ""),
      });
    } else if (/^[-*]\s/.test(line)) {
      if (!list) list = [];
      list.push(line.replace(/^[-*]\s/, ""));
    } else if (line.trim() === "") {
      flushList();
    } else {
      flushList();
      blocks.push({ type: "p", text: line });
    }
  }
  flushList();

  return (
    <div className={cn("space-y-2.5", className)}>
      {blocks.map((b, i) => {
        if (b.type === "h") {
          const cls =
            b.level === 1
              ? "text-base font-bold text-slate-900"
              : b.level === 2
              ? "mt-1 text-sm font-semibold uppercase tracking-wide text-primary-700"
              : "text-sm font-semibold text-slate-700";
          return (
            <p key={i} className={cls}>
              {renderInline(b.text)}
            </p>
          );
        }
        if (b.type === "ul") {
          return (
            <ul key={i} className="space-y-1.5">
              {b.items.map((it, j) => (
                <li
                  key={j}
                  className="flex gap-2 text-sm leading-relaxed text-slate-600"
                >
                  <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-primary-400" />
                  <span>{renderInline(it)}</span>
                </li>
              ))}
            </ul>
          );
        }
        return (
          <p key={i} className="text-sm leading-relaxed text-slate-600">
            {renderInline(b.text)}
          </p>
        );
      })}
    </div>
  );
}
