module.exports = {
  extends: ['@commitlint/config-conventional'],
  plugins: [{
    rules: {
      'req-reference': (parsed) => {
        if (!['feat', 'fix', 'test'].includes(parsed.type)) return [true];
        const valid = /\((?:BR|UR|FR|NFR)-\d{3}(?:@v\d+)?(?:,\s*(?:BR|UR|FR|NFR)-\d{3}(?:@v\d+)?)*\)/.test(parsed.header);
        return [valid, 'feat/fix/test must include a REQ reference, e.g. (FR-001)'];
      }
    }
  }],
  rules: {
    'req-reference': [2, 'always'],
    'header-max-length': [2, 'always', 240],
    'body-max-line-length': [0]
  }
};
