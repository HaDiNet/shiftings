const Configuration = {
  /*
   * Resolve and load @commitlint/config-conventional from node_modules.
   * Referenced packages must be installed
   */
  extends: ["@commitlint/config-conventional"],
  // config-conventional implements conventional commits rules as defined at https://www.conventionalcommits.org

  /*
   * Any rules defined here will override rules from @commitlint/config-conventional
   */
  rules: {
    "type-enum": [1, "always", ['build', 'chore', 'ci', 'docs', 'feat', 'fix', 'perf', 'refactor', 'revert', 'style', 'test']],
    "header-trim": [2, "always"],
    "reference-empty": [2, "never"],
  },

  /*
   * Array of functions that return true if commitlint should ignore the given message.
   * Given array is merged with predefined functions, which consist of matchers like:
   *
   * - 'Merge pull request', 'Merge X into Y' or 'Merge branch X'
   * - 'Revert X'
   * - 'v1.2.3' (ie semver matcher)
   * - 'Automatic merge X' or 'Auto-merged X into Y'
   *
   * To see full list, check https://github.com/conventional-changelog/commitlint/blob/master/%40commitlint/is-ignored/src/defaults.ts.
   * To disable those ignores and run rules always, set `defaultIgnores: false` as shown below.
   */
  ignores: [(commit) => commit === ""],
  /*
   * Whether commitlint uses the default ignore rules, see the description above.
   */
  defaultIgnores: true,

  /*
   * Custom URL to show upon failure
   */
  helpUrl:
    "",
};

export default Configuration;
