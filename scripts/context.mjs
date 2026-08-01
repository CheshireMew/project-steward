#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PRODUCT_NAMES = ['PRODUCT.md', 'Product.md', 'product.md'];
const DESIGN_NAMES = ['DESIGN.md', 'Design.md', 'design.md'];
const CONTEXT_DIRS = ['', '.agents/context', 'docs'];
const CONTEXT_ROOT_MARKERS = ['.git', 'pnpm-workspace.yaml', 'turbo.json', 'nx.json', 'lerna.json'];
const PROJECT_MARKERS = [
  'package.json',
  'pyproject.toml',
  'Cargo.toml',
  'go.mod',
  'pubspec.yaml',
  'build.gradle',
  'build.gradle.kts',
  'AndroidManifest.xml',
];

function exists(target) {
  try {
    return fs.existsSync(target);
  } catch {
    return false;
  }
}

function isFile(target) {
  try {
    return fs.statSync(target).isFile();
  } catch {
    return false;
  }
}

function safeRead(target) {
  try {
    return fs.readFileSync(target, 'utf8');
  } catch {
    return null;
  }
}

function parentsFrom(start) {
  const result = [];
  let current = path.resolve(start);
  while (true) {
    result.push(current);
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return result;
}

function hasAny(dir, names) {
  return names.some(name => exists(path.join(dir, name)));
}

function findContextRoot(start, cwd) {
  const chain = parentsFrom(start);
  const gitRoot = chain.find(dir => exists(path.join(dir, '.git')));
  if (gitRoot) return { path: gitRoot, reason: 'parent-git-context' };

  const workspaceRoot = chain.find(dir => hasAny(dir, CONTEXT_ROOT_MARKERS.slice(1)));
  if (workspaceRoot) return { path: workspaceRoot, reason: 'workspace-marker-context' };

  const absCwd = path.resolve(cwd);
  const withinCwd = path.relative(absCwd, start);
  return {
    path: !withinCwd.startsWith('..') && !path.isAbsolute(withinCwd) ? absCwd : start,
    reason: 'task-context',
  };
}

function firstContextFile(root, names) {
  for (const contextDir of CONTEXT_DIRS) {
    for (const name of names) {
      const candidate = path.join(root, contextDir, name);
      if (isFile(candidate)) return candidate;
    }
  }
  return null;
}

function hasContext(root) {
  return Boolean(firstContextFile(root, PRODUCT_NAMES) || firstContextFile(root, DESIGN_NAMES));
}

function findProjectRoot(start, contextRoot) {
  for (const dir of parentsFrom(start)) {
    if (hasContext(dir) || hasAny(dir, PROJECT_MARKERS)) return dir;
    if (path.resolve(dir) === path.resolve(contextRoot)) break;
  }
  return path.resolve(start);
}

function parseArgs(argv) {
  let target = null;
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--target') {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error('--target requires a path');
      target = value;
      index += 1;
    } else if (arg === '--help' || arg === '-h') {
      return { help: true, target: null };
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return { help: false, target };
}

function resolveTarget(cwd, targetArg) {
  if (!targetArg) return path.resolve(cwd);
  const resolved = path.isAbsolute(targetArg) ? path.normalize(targetArg) : path.resolve(cwd, targetArg);
  if (!exists(resolved)) throw new Error(`Target does not exist: ${resolved}`);
  return isFile(resolved) ? path.dirname(resolved) : resolved;
}

export function resolveProjectContext(cwd = process.cwd(), options = {}) {
  const targetDir = resolveTarget(cwd, options.target ?? null);
  const contextBoundary = findContextRoot(targetDir, cwd);
  const contextRoot = contextBoundary.path;
  const projectRoot = findProjectRoot(targetDir, contextRoot);

  const projectProduct = firstContextFile(projectRoot, PRODUCT_NAMES);
  const projectDesign = firstContextFile(projectRoot, DESIGN_NAMES);
  const rootProduct = path.resolve(projectRoot) === path.resolve(contextRoot)
    ? null
    : firstContextFile(contextRoot, PRODUCT_NAMES);
  const rootDesign = path.resolve(projectRoot) === path.resolve(contextRoot)
    ? null
    : firstContextFile(contextRoot, DESIGN_NAMES);

  const productPath = projectProduct || rootProduct;
  const designPath = projectDesign || rootDesign;

  return {
    cwd: path.resolve(cwd),
    targetDir,
    projectRoot,
    contextRoot,
    contextRootReason: contextBoundary.reason,
    contextRootGrantsGitCapability: false,
    productPath,
    productScope: projectProduct ? 'project' : rootProduct ? 'shared-context-fallback' : null,
    designPath,
    designScope: projectDesign ? 'project' : rootDesign ? 'shared-context-fallback' : null,
    product: productPath ? safeRead(productPath) : null,
    design: designPath ? safeRead(designPath) : null,
  };
}

function printContext(context) {
  const metadata = {
    cwd: context.cwd,
    targetDir: context.targetDir,
    projectRoot: context.projectRoot,
    contextRoot: context.contextRoot,
    contextRootReason: context.contextRootReason,
    contextRootGrantsGitCapability: context.contextRootGrantsGitCapability,
    productPath: context.productPath,
    productScope: context.productScope,
    designPath: context.designPath,
    designScope: context.designScope,
  };

  const parts = [`RESOLVED_CONTEXT:\n${JSON.stringify(metadata, null, 2)}`];
  if (context.product) parts.push(`# PRODUCT.md\n\n${context.product.trim()}`);
  if (context.design) parts.push(`# DESIGN.md\n\n${context.design.trim()}`);
  if (!context.product && !context.design) {
    parts.push(
      'NO_PROJECT_CONTEXT: No PRODUCT.md or DESIGN.md was found for the resolved project. ' +
      'Continue scoped work from the target code and user-provided materials; do not create context files unless the user asks.',
    );
  }
  process.stdout.write(`${parts.join('\n\n---\n\n')}\n`);
}

function invokedAsScript() {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    return fs.realpathSync(entry) === fs.realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
}

if (invokedAsScript()) {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (options.help) {
      process.stdout.write('Usage: node context.mjs [--target <file-or-directory>]\n');
      process.exit(0);
    }
    printContext(resolveProjectContext(process.cwd(), options));
  } catch (error) {
    process.stderr.write(`CONTEXT_ERROR: ${error.message}\n`);
    process.exit(1);
  }
}
