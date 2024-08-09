```{mermaid}
flowchart TD
    node1["Binarize"]
    node2["Convert CINEs"]
    node4["Find bubbles"]
    node5["Find tracks"]
    node10["Process tracks"]
    node12["Find contours"]
    node1-->node12
    node2-->node1
    node12-->node4
    node4-->node5
    node5-->node10
    style node1 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
    style node2 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
    style node4 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
    style node5 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
    style node10 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
    style node12 stroke-width:4px,stroke-dasharray: 0,stroke:#D50000
```
