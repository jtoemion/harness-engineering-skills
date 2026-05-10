import { pipeline, env } from '@huggingface/transformers';

env.allowLocalModels = true;
env.cacheDir = '.cache';

let classifier = null;

async function initPipeline() {
  if (!classifier) {
    console.error('[INIT] Loading watch model...');
    classifier = await pipeline('zero-shot-classification', 'Xenova/nli-deberta-v3-base');
    console.error('[INIT] Model loaded');
  }
  return classifier;
}

const WATCH_PATTERNS = [
  { id: 'claim-without-verification', hypothesis: 'Agent is claiming work is complete, fixed, or passing without running verification commands' },
  { id: 'skip-session-close', hypothesis: 'Agent is about to end the session without running the mandatory session close pipeline' },
  { id: 'skip-skill-steps', hypothesis: 'Agent is skipping steps or phases in a skill workflow (e.g., jumping to implementation without planning, jumping to completion without review)' },
  { id: 'scope-creep', hypothesis: 'Agent is about to touch files or modify areas outside the declared task scope' },
  { id: 'stale-memory', hypothesis: 'Agent is not updating project memory (.memory/) — stale memory leads to wrong decisions' },
  { id: 'hidden-assumptions', hypothesis: 'Agent is making hidden assumptions instead of surfacing them first (e.g., assuming library is installed, assuming correct config, assuming API format)' },
  { id: 'skip-mistakes-check', hypothesis: 'Agent is about to write code without checking for known mistakes that could cause the same failure' },
  { id: 'subagent-bypass', hypothesis: 'Agent is not using proper subagent protocol (skipping SUBAGENT_BRIEF.md or reading raw results instead of SUBAGENT_RESULT.md)' },
  { id: 'force-push-risk', hypothesis: 'Agent is about to run a destructive git command like force push, hard reset, or rebase that could lose work' },
  { id: 'no-evidence-claim', hypothesis: 'Agent is asserting something as fact without showing evidence (e.g., says "this works" without running the actual command)' },
  { id: 'mode-violation', hypothesis: 'Agent is running FULL-mode-only operations (like session close, cold start, mistakes logging) in QUICK mode' },
  { id: 'skip-checkpoint', hypothesis: 'Agent is about to wrap up without creating a checkpoint for the current task' },
];

async function watch(input) {
  const classifier = await initPipeline();
  const labels = WATCH_PATTERNS.map(p => p.hypothesis);

  const result = await classifier(input, labels, { multi_label: true });

  const alerts = [];
  for (let i = 0; i < result.labels.length; i++) {
    const score = result.scores[i];
    if (score >= 0.5) {
      const pattern = WATCH_PATTERNS.find(p => p.hypothesis === result.labels[i]);
      alerts.push({ pattern_id: pattern.id, confidence: Math.round(score * 100) / 100 });
    }
  }

  return {
    alerts,
    gate: alerts.length === 0 ? 'PASS' : 'WARN',
    reason: 'nli-watch',
  };
}

async function main() {
  await initPipeline();

  const stdin = process.stdin;
  stdin.setEncoding('utf-8');
  let buffer = '';

  for await (const chunk of stdin) {
    buffer += chunk;
    let newlineIdx;
    while ((newlineIdx = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, newlineIdx).trim();
      buffer = buffer.slice(newlineIdx + 1);
      if (!line) continue;
      try {
        const { input } = JSON.parse(line);
        const result = await watch(input);
        console.log(JSON.stringify(result));
      } catch (e) {
        console.error(JSON.stringify({ error: e.message }));
      }
    }
  }
}

main().catch(e => { console.error(JSON.stringify({ fatal: e.message })); process.exit(1); });