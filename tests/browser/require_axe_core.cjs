'use strict';

const fs = require('node:fs');

function resolveAxeCorePath(env = process.env) {
  let axePath = env.AXE_CORE_PATH;
  if (!axePath) {
    try { axePath = require.resolve('axe-core/axe.min.js'); } catch {}
  }
  return axePath || null;
}

function requireAxeCorePath(env = process.env) {
  const axePath = resolveAxeCorePath(env);
  if (!axePath) {
    throw new Error(
      'axe-core is required for the browser accessibility audit and will not be skipped silently. ' +
      'Set AXE_CORE_PATH to an existing axe.min.js, or install the axe-core package so ' +
      'require.resolve("axe-core/axe.min.js") succeeds.'
    );
  }
  if (!fs.existsSync(axePath)) {
    throw new Error(
      `axe-core is required for the browser accessibility audit, but AXE_CORE_PATH does not exist: ${axePath}`
    );
  }
  return axePath;
}

module.exports = {resolveAxeCorePath, requireAxeCorePath};

if (require.main === module) {
  try {
    process.stdout.write(requireAxeCorePath() + '\n');
  } catch (error) {
    process.stderr.write(error.message + '\n');
    process.exitCode = 1;
  }
}
