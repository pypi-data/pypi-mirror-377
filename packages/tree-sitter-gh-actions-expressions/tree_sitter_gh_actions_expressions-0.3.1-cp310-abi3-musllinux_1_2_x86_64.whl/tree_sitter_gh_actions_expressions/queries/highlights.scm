(boolean) @boolean

(null) @constant.builtin

[
  (number)
  (format_index)
] @number

[
  (string)
  (format_string)
] @string

(format_variable
  [
    "{"
    "}"
  ] @punctuation.bracket)

(scape_sequence) @string.escape

(context
  (identifier) @function.builtin
  (#any-of? @function.builtin
    "github" "env" "vars" "job" "jobs" "steps" "runner" "secrets" "strategy" "matrix" "needs"
    "inputs"))

(property
  [
    (identifier)
    (asterisk)
  ] @variable.member)

(property_deref) @punctuation.delimiter

(index) @punctuation.delimiter

(function_call
  function: (identifier) @function)

(function_call
  [
    "("
    ")"
  ] @punctuation.bracket)

"," @punctuation.delimiter

(delimited_expression
  [
    "${{"
    "}}"
  ] @punctuation.bracket)

(logical_group
  [
    "("
    ")"
  ] @punctuation.bracket)

[
  (operator)
  (not)
] @operator
