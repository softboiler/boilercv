```{mermaid}
flowchart TD
 node1["Binarize"]
 node2["Convert CINEs"]
 node6["Fill contours"]
 node7["Find contours"]
 node8["Find bubbles"]
 node9["Link bubbles"]
 node10["Correlate"]
 node11["Process data"]
 node12["Check binarized"]
 node13["Check filled"]
 node14["Check gray"]
 node1-->node6
 node1-->node7
 node1-->node12
 node1-->node13
 node2-->node1
 node2-->node14
 node6-->node8
 node6-->node9
 node7-->node6
 node7-->node8
 node8-->node9
 node9-->node10
 node11-->node9
 node11-->node10
```
