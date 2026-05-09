import { pipeline, env } from '@xenova/transformers';

env.allowLocalModels = false;

const args = process.argv.slice(2);
const mode = args.includes('--route') ? 'route' : args.includes('--validate') ? 'validate' : 'route';

let classifier = null;

async function initPipeline() {
  if (!classifier) {
    classifier = await pipeline('text-generation', 'onnx-community/Qwen2.5-0.5B-Instruct', {
      quantization_config: { quantization_type: 'int8' },
    });
  }
  return classifier;
}

const SKILLS = [
  { id: 'brainstorming', triggers: ['create feature', 'add functionality', 'modify behavior'] },
  { id: 'systematic-debugging', triggers: ['bug', 'fix error', 'unexpected behavior'] },
  { id: 'test-driven-development', triggers: ['implement feature', 'bugfix'] },
  { id: 'requesting-code-review', triggers: ['complete task', 'implement major feature'] },
  { id: 'finishing-a-development-branch', triggers: ['implementation complete', 'tests pass'] },
  { id: 'architectural-impact', triggers: ['data change', 'new feature', 'business logic', 'api endpoint'] },
  { id: 'frontend-avant-garde', triggers: ['ui', 'ux', 'visual design', 'styling', 'animation'] },
  { id: 'subagent-driven-development', triggers: ['implementation plan', 'independent tasks'] },
  { id: 'verification-before-completion', triggers: ['claim work complete', 'verify'] },
];

function buildRouterPrompt(input, state) {
  const skillList = SKILLS.map(s => `  - ${s.id}: ${s.triggers.join(', ')}`).join('\n');
  return `<|im_start|>user
Classify the task. Reply with JSON only: {"skill_id": "...", "confidence": 0.0-1.0, "gate": "PASS|WARN|BLOCK", "reason": "..."}

Skills:
${skillList}

Input: ${input}
State: ${JSON.stringify(state)}<|im_end|>
<|im_start|>assistant
`;
}

function buildValidatorPrompt(state) {
  return `<|im_start|>user
Validate flow sequence. Reply JSON: {"valid": true/false, "gate": "PASS|WARN|BLOCK", "reason": "..."}

Valid sequences: pre-task → skill → checkpoint → verification → next-task
Allowed: pre-task, skill, checkpoint, verification, next-task, start, end

State: ${JSON.stringify(state)}<|im_end|>
<|im_start|>assistant
`;
}

async function classifyRoute(input, state) {
  const generate = await initPipeline();
  const prompt = buildRouterPrompt(input, state);
  const result = await generate(prompt, {
    max_new_tokens: 80,
    temperature: 0.1,
    do_sample: true,
  });
  const text = result[0].generated_text;
  const jsonMatch = text.match(/\{[^}]+\}/s);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[0]);
    } catch {
      return { skill_id: null, confidence: 0, gate: 'WARN', reason: 'parse error' };
    }
  }
  return { skill_id: null, confidence: 0, gate: 'WARN', reason: 'no json in response' };
}

async function validateFlow(state) {
  const generate = await initPipeline();
  const prompt = buildValidatorPrompt(state);
  const result = await generate(prompt, {
    max_new_tokens: 80,
    temperature: 0.1,
    do_sample: true,
  });
  const text = result[0].generated_text;
  const jsonMatch = text.match(/\{[^}]+\}/s);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[0]);
    } catch {
      return { valid: false, gate: 'WARN', reason: 'parse error' };
    }
  }
  return { valid: false, gate: 'WARN', reason: 'no json in response' };
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
        const result = mode === 'validate'
          ? await validateFlow(state)
          : await classifyRoute(input, state);
        console.log(JSON.stringify(result));
      } catch (e) {
        console.error(JSON.stringify({ error: e.message }));
      }
    }
  }
}

main().catch(e => { console.error(JSON.stringify({ fatal: e.message })); process.exit(1); });
