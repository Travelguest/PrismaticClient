<template>
  <div>
    <!--    {{corrDistribution}}-->
    <!--    <br><br>-->
    <!--    {{corrCluster}}-->
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
  emits: [
    'get-correlation-matrix',
  ],
  data() {
    return {
      svg: null,
      width: 0,
      height: 1620,
      margin: { top: 10, right: 10, bottom: 10, left: 10 },

      distWidth: 100,
      distHeight: 150,
      distPadding: 11.5,

      color: d3.schemeTableau10,

      yearSelected: '2020',
      correlationRange: [0.6, 1],
      correlationMarks: {0.6: '0.6', 0: '0', 1: '1'},
      correlatedStocks: [],
    }
  },
  watch: {
    corrDistribution: function() {
      this.renderGraph();
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
      this.svg
          .selectAll('graph')
          .data(Object.entries((this.corrCluster)))
          .enter()
          .append('g')
          .attr('class', 'dist')
          .attr('transform', (_, i) => `translate(${0},${this.distPadding+(this.distHeight+this.distPadding) * i})`);

      console.log(Object.entries((this.corrCluster)))
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

      // Distribution charts container
      this.svg
          .selectAll('.dist')
          // sort to have 2020 be the first year to display
          .data(Object.entries(this.corrDistribution).sort((a, b)=>(a[0]<b[0]?1: -1)))
          .enter()
          .append('g')
          .attr('class', 'dist')
          .attr('transform', (_, i) => `translate(${0},${this.distPadding+(this.distHeight+this.distPadding) * i})`)
          .each(function(data, i, containers) {
            let container = d3.select(containers[i]);
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
                .call(g => g.selectAll(".tick text")
                    .attr("dx", -5)
                    .attr("dy", 4));
            // y-axis
            container
                .append("g")
                .attr("class", "yAxis")
                .attr("transform", `translate(${_this.distWidth},0)`)
                .call(d3.axisRight(distY).ticks(3));
            // index area plot
            container
                .append("path")
                .datum(data[1].sci)
                .style("stroke", "rgba(80,161,255,0.10)")
                .style("fill", "rgba(80,161,255,0.10)")
                .attr("d", indexArea);
            // stock line plots
            container
                .append("g")
                .selectAll('.stockLine')
                .data(Object.entries(data[1]).filter((d) => d[0] !== 'sci'))
                // .data(Object.entries(data[1]))
                .enter()
                .append('path')
                .attr('class', 'stock-line')
                .attr('d', (d) => stockLine(d[1]))
                .attr('fill', 'none')
                .attr('stroke-width', '2px')
                .attr('stroke', 'cornflowerblue');

          });
    },
    onCorrelationSliderChange(val) {
      this.correlationMarks = {0: '0'};
      this.correlationMarks[val[0]] = ''+val[0];
      this.correlationMarks[val[1]] = ''+val[1];
    },
    onClusterButtonClick() {
      this.$emit('get-correlation-matrix');
    },
  }
}
</script>

<style scoped>

</style>
