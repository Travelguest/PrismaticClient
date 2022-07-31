# Abstract
Exploring financial correlation clusters allows investors to avoid undertaking excessive risks and discover investment
alternatives. 
Strongly correlated assets suggest a tendency for them to gravitate towards a similar set of economic factors. Therefore, a
plethora of research has focused on developing technical features to capture the dynamic comovement of stock prices. However, this
analytical task faces substantial challenges arising from a large number of pairwise comparisons, the dynamic nature of correlation,
and the ambiguity in understanding implication. When making investment decisions, investors also apply their knowledge of business
relationships for extrapolation purposes, albeit promising technical analysis. In this work, we propose Prismatic, a visual analytics
system that integrates historical performance analysis and business knowledge graph exploration to interactively cluster the dynamic
financial correlations. Prismatic facilitates three key analytical processes: cluster exploration by holistically overviewing the changing
structure of clusters, cluster verification by shedding lights on the temporal patterns in correlations at different time scales, and cluster
generation by embedding the business knowledge graph to contextualize the underlying relationships. We evaluate the usefulness and
effectiveness of Prismatic through two case studies and extensive interviews with domain experts.

## Client
The client services are provided by Vue 3. 
All codes below should be run under the "client" folder.

### Client Setup
The packages are handled by npm, and specified in the package.json.
```
$ npm install
```

### Client activation
The client is served at http://localhost:8080/.
Notice that the framework supports hot-reloads, so that the changes on DOM are applied automatically and do not require reloads.
```
# Compiles and hot-reloads for development
$ npm run serve

# Compiles and minifies for production
$ npm run build
```
