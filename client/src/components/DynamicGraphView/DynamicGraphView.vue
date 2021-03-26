<template>
  <div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'DynamicGraphView',
  components: {},
  props: {
    corrDistribution: Object,
    corrCluster: Object,
  },
  emits: ['clickedYear'],
  data() {
    return {
      svg: null,
      width: 0,
      height: 1175,
      margin: { top: 10, right: 10, bottom: 10, left: 10 },

      distWidth: 80,
      distHeight: 105,
      distPaddingHeight: 12,
      distPaddingWidth: 20,

      graphMaxNodes: 40,

      color: d3.schemeTableau10,

      yearSelected: '2020',
      correlationRange: [0.6, 1],
      correlationMarks: {0.6: '0.6', 0: '0', 1: '1'},
      correlatedStocks: [],
    }
  },
  watch: {
    corrDistribution: function() {
      this.svg.selectAll('.dist').remove();
      this.renderDistChart();
    },
    corrCluster: function() {
      this.svg.selectAll('.graph').remove();
      this.renderNodeLink();
    },
    periodRange: function() {
      this.$emit('update-period-range', this.periodRange);
    }
  },
  computed: {
  },
  mounted: function () {
    this.initGraph();
    this.renderGraph();
  },
  methods: {
    initGraph() {
      this.width = this.$el.clientWidth;

      this.svg = d3
          .select(this.$el)
          .append("svg")
          .attr("viewBox", [0, 0, this.width, this.height]);
    },
    renderGraph() {
      // Remove all groups in svg
      this.svg.selectAll("g").remove();

      this.renderNodeLink();
      this.renderDistChart();
    },
    renderNodeLink(){
      let _this = this;
      let graphWidth = this.width-this.distWidth-this.distPaddingWidth*3;
      let graphHeight = this.distHeight+this.distPaddingHeight;

      let topNodes = Object.fromEntries(
          Object.entries(this.corrCluster)
              .map(([k, v]) => [
                k,
                Object.entries(v.betweenness)
                    .sort((a, b)=>(a[1]<b[1]?1: -1)) // descending order
                    .slice(-this.graphMaxNodes) // select top n
                    .map(x => x[0]) // keep only keys
              ]));

      let graphX = Object.fromEntries(
          Object.entries(this.corrCluster)
              .map(([k, v]) => [k, v.nodes.filter((x) => topNodes[k].includes(x))])
              .map(([k, v]) => [k, d3.scalePoint()
                  .domain(v)
                  .range([0, graphWidth])
              ]));

      let graphY = d3.scalePoint()
          .domain(Object.keys(this.corrCluster).sort().reverse())
          .range([this.distHeight*0.75, this.distHeight*0.75+graphHeight*9]);

      let container = this.svg
          .selectAll('.graph')
          // .data(Object.entries(this.corrCluster).sort((a, b)=>(a[0]<b[0]?1: -1)))
          .data(Object.keys(this.corrCluster).sort().reverse())
          .enter()
          .append('g')
          .attr('class', 'graph')
          .attr('transform', d => `translate(${this.distWidth+this.distPaddingWidth*2}, ${graphY(d)})`);

      container
          .append("rect")
          .attr('class', 'background')
          .attr('y', -this.distHeight*0.68)
          .attr("width", graphWidth)
          .attr("height", graphHeight-this.distPaddingHeight)
          .style("fill", "#D6DBDF")
          .style('opacity', 0.25)
          .on("click", (_, d) => {
            _this.$emit("clickedYear", d, topNodes[d]);
          });


      // draw the node link diagram
      container.each( (d, i, c) => {
        let container = d3.select(c[i]);

        // draw the xAxis
        container
            .append("g")
            .attr("class", "xAxis")
            .call(d3.axisBottom(graphX[d]))
            .call(g => g.selectAll(".tick").remove());

        // draw node to the axis
        container
            .selectAll(".node")
            .data(topNodes[d])
            .enter()
            .append("circle")
            .attr("class", "node")
            .attr('id', (node) => node)
            .attr("cx", (node) => graphX[d](node))
            .attr("r", '4px')
            .style('fill', 'cornflowerblue');

        // draw a vertical line to link the same node in last year
        if ( i !== 0 ) {
          let lastD = ""+(2021-i);
          container
              .selectAll(".linkage")
              .data(topNodes[d].filter((x) => topNodes[lastD].includes(x)))
              .enter()
              .append("path")
              .attr("class", "linkage")
              .attr('id', (node) => node)
              .attr('d', (node) => {
                // provide more points for curvy effect
                let path = [
                  {x: graphX[lastD](node), y:-graphHeight},
                  {x: graphX[lastD](node), y:-graphHeight+20},
                  {x: graphX[d](node), y:-20},
                  {x: graphX[d](node), y:0}
                ]
                return d3.line()
                    .curve(d3.curveBasis)
                    .x(d => d.x)
                    .y(d => d.y)(path)
              })
              .attr("stroke", "cornflowerblue")
              .attr('fill', 'none');
        }
      });
      this.svg.selectAll('.node').raise();
    },
    renderDistChart(){
      let _this = this;
      let distX = d3.scaleLinear().domain([799, 0]).range([0, this.distWidth]); // x is count
      let distY = d3.scaleLinear().domain([1, -0.5]).range([0, this.distHeight]); // y is correlation
      let stockLine = d3.line().curve(d3.curveCatmullRom)
          .x((d) => distX(d))
          .y((_, i) => distY(-0.5+i*0.05));
      let indexArea = d3
          .area()
          .x0(distX(0))
          .x1((d) => distX(d))
          .y((_, i) => distY(-0.5+i*0.05));
      let removedDistTickText = false;

      // Distribution charts container
      this.svg
          .selectAll('.dist')
          // sort to have 2020 be the first year to display
          .data(Object.entries(this.corrDistribution).sort((a, b)=>(a[0]<b[0]?1: -1)))
          .enter()
          .append('g')
          .attr('class', 'dist')
          .attr('transform', (_, i) =>
              `translate(${0},${this.distPaddingHeight+(this.distHeight+this.distPaddingHeight) * i})`
          )
          .each((d, i, c) => {
            let container = d3.select(c[i]);
            // x-axis
            container
                .append("g")
                .attr("class", "xAxis")
                .attr("transform", `translate(0, ${_this.distHeight})`)
                .call(d3.axisTop(distX)
                    .ticks(4)
                    .tickSize(_this.distHeight))
                .call(g => g.select(".domain").remove())
                .call(g => g.selectAll(".tick line")
                    .attr("stroke-opacity", 0.2)
                    .attr("stroke-dasharray", "1,1"))
                .call(g => {
                  g.selectAll(".tick text").attr("dx", 0).attr("dy", 0)
                  if (removedDistTickText) {
                    g.selectAll(".tick text").remove();
                  } else {
                    removedDistTickText = true;
                  }
                });
            // y-axis
            container
                .append("g")
                .attr("class", "yAxis")
                .attr("transform", `translate(${_this.distWidth},0)`)
                .call(d3.axisRight(distY).ticks(3));
            // index area plot
            container
                .append("path")
                .datum(d[1].sci)
                .style("stroke", "rgba(80,161,255,0.10)")
                .style("fill", "rgba(80,161,255,0.10)")
                .attr("d", indexArea);
            // stock line plots
            container
                .append("g")
                .selectAll('.stockLine')
                .data(Object.entries(d[1]).filter((d) => d[0] !== 'sci'))
                .enter()
                .append('path')
                .attr('class', 'stock-line')
                .attr('d', (d) => stockLine(d[1]))
                .attr('fill', 'none')
                .attr('stroke-width', '2px')
                .attr('stroke', 'cornflowerblue');
          });
    }
  }
}
</script>

<style scoped>

</style>
