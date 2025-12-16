import { motion } from 'framer-motion';
import { FileText, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface AnalysisNarrativeProps {
  narrative: string;
  loading?: boolean;
}

export default function AnalysisNarrative({ narrative, loading }: AnalysisNarrativeProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(narrative);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-4 bg-dark-600 rounded" style={{ width: `${Math.random() * 40 + 60}%` }} />
          ))}
        </div>
      </div>
    );
  }

  // Simple markdown-like parsing
  const parseContent = (text: string) => {
    return text.split('\n').map((line, idx) => {
      // Headers
      if (line.startsWith('## ')) {
        return (
          <h2 key={idx} className="font-display text-xl font-bold text-neon-cyan mt-6 mb-3 first:mt-0">
            {line.replace('## ', '')}
          </h2>
        );
      }
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} className="font-display text-lg font-bold text-white mt-4 mb-2">
            {line.replace('### ', '')}
          </h3>
        );
      }
      // Horizontal rule
      if (line.startsWith('---')) {
        return <hr key={idx} className="border-dark-600 my-4" />;
      }
      // Bold text handling
      if (line.includes('**')) {
        const parts = line.split(/\*\*(.*?)\*\*/g);
        return (
          <p key={idx} className="text-gray-300 leading-relaxed mb-2">
            {parts.map((part, i) => 
              i % 2 === 1 ? <strong key={i} className="text-white font-semibold">{part}</strong> : part
            )}
          </p>
        );
      }
      // Table rows
      if (line.includes('|')) {
        const cells = line.split('|').filter(c => c.trim());
        if (cells.length >= 2 && !line.includes('---')) {
          return (
            <div key={idx} className="flex border-b border-dark-600 py-2">
              <span className="w-1/2 text-gray-400 text-sm">{cells[0].trim()}</span>
              <span className="w-1/2 text-white font-mono text-sm">{cells[1].trim()}</span>
            </div>
          );
        }
        return null;
      }
      // Italic text
      if (line.startsWith('*') && line.endsWith('*')) {
        return (
          <p key={idx} className="text-gray-400 italic text-sm mb-2">
            {line.replace(/\*/g, '')}
          </p>
        );
      }
      // Regular paragraph
      if (line.trim()) {
        return (
          <p key={idx} className="text-gray-300 leading-relaxed mb-2">
            {line}
          </p>
        );
      }
      return null;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass rounded-2xl border border-neon-cyan/20 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-600 bg-dark-800/50">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-neon-cyan" />
          <h3 className="font-display font-bold text-white">Analysis Report</h3>
        </div>
        <button
          onClick={handleCopy}
          className={clsx(
            "flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-all",
            copied 
              ? "bg-bullish/20 text-bullish" 
              : "bg-dark-600 text-gray-400 hover:text-white hover:bg-dark-500"
          )}
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy
            </>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="p-6 max-h-[600px] overflow-y-auto">
        <div className="prose prose-invert max-w-none">
          {parseContent(narrative)}
        </div>
      </div>
    </motion.div>
  );
}

