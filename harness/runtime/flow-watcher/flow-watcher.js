import { pipeline, env } from '@huggingface/transformers';

env.allowLocalModels = true;
env.cacheDir = '.cache';

let classifier = null;

async function initPipeline() {
  if (!classifier) {
    console.error('[INIT] Loading model...');
    classifier = await pipeline('text-generation', 'onnx-community/Qwen2.5-0.5B-Instruct', { quantized: false });
    console.error('[INIT] Model loaded');
  }
  return classifier;
}

const SKILLS = [
  { id: 'brainstorming', keywords: ['create', 'feature', 'add', 'functionality', 'modify'] },
  { id: 'systematic-debugging', keywords: ['bug', 'fix', 'error', 'unexpected', 'issue', 'problem'] },
  { id: 'test-driven-development', keywords: ['test', 'tdd', 'write test', 'red green'] },
  { id: 'requesting-code-review', keywords: ['review', 'pr', 'pull request', 'complete'] },
  { id: 'architectural-impact', keywords: ['data', 'database', 'api', 'endpoint', 'architecture'] },
  { id: 'frontend-avant-garde', keywords: ['ui', 'ux', 'css', 'style', 'design', 'visual'] },
  { id: 'verification-before-completion', keywords: ['verify', 'complete', 'done', 'working'] },
];

function keywordMatch(input) {
  const lower = input.toLowerCase();
  for (const skill of SKILLS) {
    for (const kw of skill.keywords) {
      if (lower.includes(kw)) {
        return { skill_id: skill.id, confidence: 0.75, gate: 'PASS', reason: `keyword match: ${kw}` };
      }
    }
  }
  return null;
}

function parseResponse(text) {
  // Check for skill name ONLY after "assistant" (the model's response)
  const assistantIndex = text.indexOf('<|im_start|>assistant');
  if (assistantIndex === -1) {
    // Try "assistant" without the tags
    const altIndex = text.indexOf('assistant');
    if (altIndex !== -1) {
      const responsePart = text.substring(altIndex);
      for (const skill of SKILLS) {
        if (responsePart.includes(skill.id)) {
          return { skill_id: skill.id, confidence: 0.7, gate: 'PASS', reason: 'model matched' };
        }
      }
    }
    return null;
  }

  const responsePart = text.substring(assistantIndex);
  for (const skill of SKILLS) {
    if (responsePart.includes(skill.id)) {
      return { skill_id: skill.id, confidence: 0.7, gate: 'PASS', reason: 'model matched' };
    }
  }

  return null;
}

async function classifyRoute(input, state) {
  const generate = await initPipeline();

  const prompt = `<|im_start|>user
Classify: "${input}"
Reply with skill_id only from: ${SKILLS.map(s => s.id).join(', ')}<|im_end|>
<|im_start|>assistant
`;

  const result = await generate(prompt, { max_new_tokens: 60, temperature: 0.1 });
  const text = result[0].generated_text;
  console.error('[RAW]', text.substring(0, 300));

  const parsed = parseResponse(text);
  if (parsed) {
    return parsed;
  }

  // Fall back to keyword
  const kwResult = keywordMatch(input);
  if (kwResult) {
    console.error('[FALLBACK] Keyword match:', kwResult);
    return kwResult;
  }

  return { skill_id: 'karpathy-guidelines', confidence: 0.3, gate: 'PASS', reason: 'default' };
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
        const { input, state } = JSON.parse(line);
        const result = await classifyRoute(input, state);
        console.log(JSON.stringify(result));
      } catch (e) {
        console.error('[ERROR]', e.message);
      }
    }
  }
}

main().catch(e => { console.error('[FATAL]', e.message); process.exit(1); });