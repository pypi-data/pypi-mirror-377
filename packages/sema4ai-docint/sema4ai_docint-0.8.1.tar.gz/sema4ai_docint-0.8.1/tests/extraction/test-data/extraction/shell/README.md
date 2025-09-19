## Expectations

245 line items (103 sales, 142 purchases)

```
jq '.line_items | length' tests/test-data/extraction/shell/expected.json
```

sum of sales: 8,659,742.29

```
jq -r '.line_items[] | select(.buy_sell == "Sell") | .amount' tests/test-data/extraction/shell/expected.json | awk '{sum+=$1;} END {OFMT="%f";print sum;}'
```

sum of purchases: 17,526,643.89

```
jq -r '.line_items[] | select(.buy_sell == "Buy") | .amount' tests/test-data/extraction/shell/expected.json | awk '{sum+=$1;} END {OFMT="%f";print sum;}'
```
