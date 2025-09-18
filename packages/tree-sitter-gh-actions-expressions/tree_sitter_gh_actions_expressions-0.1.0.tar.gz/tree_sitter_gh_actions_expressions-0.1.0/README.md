# tree-sitter-gh-actions-expressions

[![CI][ci]](https://github.com/Hdoc1509/tree-sitter-gh-actions-expressions/actions/workflows/ci.yml)
[![discord][discord]](https://discord.gg/w7nTvsVJhm)
[![matrix][matrix]](https://matrix.to/#/#tree-sitter-chat:matrix.org)
[![crates][crates]](https://crates.io/crates/tree-sitter-gh-actions-expressions)
[![npm][npm]](https://www.npmjs.com/package/tree-sitter-gh-actions-expressions)
[![pypi][pypi]](https://pypi.org/project/tree-sitter-gh-actions-expressions)

[Tree-sitter](https://github.com/tree-sitter/tree-sitter) grammar for
[Github Actions expressions][gh-actions-expressions-docs]

## Parser requirements

- [`gitignore`](https://github.com/shunsambongi/tree-sitter-gitignore)
  (optional): for `hashFiles()` function
- [`json`](https://github.com/tree-sitter/tree-sitter-json) (optional): for
  `fromJSON()` function
- [`yaml`](https://github.com/tree-sitter/tree-sitter-yaml): injection to its
  `block_mapping_pair` node

## Usage in Editors

### Neovim

#### Requirements

- [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter)
- [Node.js](https://nodejs.org/en/download) (if ABI not compatible)
- [tree-sitter cli](https://github.com/tree-sitter/tree-sitter/tree/master/crates/cli)
  (if ABI not compatible)

#### Installation

1. Add the following to your `nvim-treesitter` configuration:

   ```lua
   local parser_config = require("nvim-treesitter.parsers").get_parser_configs()

   -- NOTE: add the parser to `parser_config` before calling `setup()`
   parser_config.gh_actions_expressions = {
     install_info = {
       url = 'https://github.com/Hdoc1509/tree-sitter-gh-actions-expressions',
       files = { "src/parser.c" },
       revision = 'release',
       -- if ABI version from neovim doesn't match the one from this grammar
       -- requires Node.js and tree-sitter cli to be installed
       requires_generate_from_grammar = true,
     },
   }

   require('nvim-treesitter.configs').setup({
     ensure_installed = {
       --- other parsers
       'gh_actions_expressions',
     },
     -- other options
   })
   ```

2. Copy the queries from [`queries`](./queries) directory to
   `queries/gh_actions_expression` directory in your `neovim` configuration
   directory:

   | With                  | Path                    |
   | --------------------- | ----------------------- |
   | Unix                  | `~/.config/nvim`        |
   | Windows               | `~/AppData/Local/nvim`  |
   | `XDG_CONFIG_HOME` set | `$XDG_CONFIG_HOME/nvim` |

### Helix

WIP

### Emacs

WIP

### In General

You can get the built files from the [`release` branch][release-branch]. If you
have specific instructions for your editor, PR's are welcome.

## Implementations

WIP

## References

- [Github Actions expressions documentation][gh-actions-expressions-docs]
- `if` conditional:
  - [run.steps\[\*\].if][gh-run-steps-if]
  - [jobs.\<job_id>.if][gh-jobs-jobid-if]
- [Gihub Actions Context documentation][gh-actions-context-docs]

## Thanks

Thanks to [@disrupted](https://github.com/disrupted) for creating
[tree-sitter-github-actions grammar](https://github.com/disrupted/tree-sitter-github-actions),
which is the base I used to create this grammar.

[ci]: https://github.com/Hdoc1509/tree-sitter-gh-actions-expressions/actions/workflows/ci.yml/badge.svg
[discord]: https://img.shields.io/discord/1063097320771698699?logo=discord&label=discord
[matrix]: https://img.shields.io/matrix/tree-sitter-chat%3Amatrix.org?logo=matrix&label=matrix
[crates]: https://img.shields.io/crates/v/tree-sitter-gh-actions-expressions?logo=rust
[npm]: https://img.shields.io/npm/v/tree-sitter-gh-actions-expressions?logo=npm
[pypi]: https://img.shields.io/pypi/v/tree-sitter-gh-actions-expressions?logo=pypi&logoColor=ffd242
[gh-actions-expressions-docs]: https://docs.github.com/en/actions/reference/evaluate-expressions-in-workflows-and-actions
[gh-run-steps-if]: https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax#runsstepsif
[gh-jobs-jobid-if]: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idif
[gh-actions-context-docs]: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
[release-branch]: https://github.com/Hdoc1509/tree-sitter-gh-actions-expressions/tree/release
