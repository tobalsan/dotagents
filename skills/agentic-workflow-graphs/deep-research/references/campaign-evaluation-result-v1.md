# Campaign evaluation result v1

[`campaign-evaluation-result-v1.schema.json`](campaign-evaluation-result-v1.schema.json) defines every `campaign-evaluate` stdout result. `continue`, `complete`, operational-limit failure, and state-error failure are closed object shapes.

Exit `0` accompanies `continue`, exit `10` accompanies `complete`, and exit `20` accompanies either failed shape.
