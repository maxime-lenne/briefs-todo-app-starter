import js from '@eslint/js';
import eslintPluginPrettier from 'eslint-plugin-prettier';
import eslintConfigPrettier from 'eslint-config-prettier';
import svelteEslint from 'eslint-plugin-svelte';
import tsEslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default [
  js.configs.recommended,
  ...svelteEslint.configs['flat/recommended'],
  ...svelteEslint.configs['flat/prettier'],
  {
    ignores: ['**/.svelte-kit', '**/node_modules', '**/build', '**/dist', '**/.venv'],
  },
  {
    files: ['**/*.svelte'],
    languageOptions: {
      parser: svelteEslint.parser,
      parserOptions: {
        parser: tsParser,
        svelteConfig: true,
        extraFileExtensions: ['.svelte'],
      },
    },
    plugins: {
      svelte: svelteEslint,
      '@typescript-eslint': tsEslint,
      prettier: eslintPluginPrettier,
    },
    rules: {
      ...svelteEslint.configs['flat/recommended'].rules,
      // TypeScript
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      // Svelte
      'svelte/require-each-key': 'error',
      'svelte/no-at-html-tags': 'warn',
      'svelte/no-target-blank': 'warn',
      'svelte/valid-compile': 'error',
      // Prettier (must be last)
      'prettier/prettier': 'error',
    },
  },
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': tsEslint,
      prettier: eslintPluginPrettier,
    },
    rules: {
      ...tsEslint.configs['eslint-recommended'].overrides[0].rules,
      ...tsEslint.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      'no-console': 'warn',
      'prefer-const': 'error',
      'prettier/prettier': 'error',
    },
  },
  eslintConfigPrettier,
];
