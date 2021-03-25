<template>
  <div>
    {{corrDistribution}}
    <br><br>
    {{corrCluster}}
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
      height: 0,
      margin: { top: 10, right: 10, bottom: 10, left: 10 },

      distContainer: null,
      distX: null,
      distY: null,
      distWidth: 100,
      distHeight: 100,

      yearSelected: '2020',
      correlationRange: [0.6, 1],
      correlationMarks: {0.6: '0.6', 0: '0', 1: '1'},
      correlatedStocks: [],
    }
  },
  watch: {
    corrDistribution: function() {
      // console.log(this.corrDistribution)
    },
    periodRange: function() {
      this.$emit('update-period-range', this.periodRange);
    }
  },
  computed: {
    stockListIndustries() {
      let set = Array.from(new Set(this.correlatedStocks.map(x => x.industry_name)));
      return set.map(x => {
        return {text: x, value: x};
      });
    },
  },
  mounted: function () {
    // this.initGraph();
    // this.renderGraph();
  },
  methods: {
    initGraph() {
      this.width = this.$el.clientWidth;
      this.height = this.$el.clientHeight;

      this.svg = d3
          .select(this.$el)
          .append("svg")
          .attr("viewBox", [0, 0, this.width, this.height]);

      this.graphContainer = this.svg
          .append("g")
          .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

      this.distX = d3.scaleLinear().domain([0, 600]).range([0, this.distWidth]).nice(); // x is count
      this.distY = d3.scaleLinear().domain([-0.4, 1]).range([0, this.distHeight]).nice(); // y is correlation
    },
    renderGraph() {
      // Remove all groups in svg
      this.svg.selectAll("g").remove();

      // Distribution charts container
      this.distContainer = this.svg
          .selectAll('.dist')
          .data(Object.entries(this.corrDistribution))
          .enter()
          .append('g')
          .attr('class', 'dist')
          .attr('transform', (_, i) => `translate(${0},${this.distHeight * i})`)
          .each(function(data, index, container) {
            container[index]
                .append("g")
                .attr("class", "xAxis")
                // .attr("transform", `translate(0,${this.innerHeight})`)
                .call(d3.axisBottom(this.distX))
            // .select(".domain")
            // .remove();

            container[index]
                .append("g")
                .attr("class", "yAxis")
                .call(d3.axisRight(this.distY))
            // .select(".domain")
            // .remove();
            console.log(container[index])
          });

      // this.cell_containers = d3.select(rowContainer)
      //     .selectAll('.cell')
      //     .data(_this.featureData)
      //     .enter()
      //     .append('g')
      //     .attr('class', 'cell')
      //     .attr('transform', d => 'translate(' + [_this.xScale(d.timestamp), 0] + ')');
      //
      // let rects = cell_containers
      //     .append('rect')
      //     .attr('width', _this.unitWidth > 1?_this.unitWidth-1: _this.unitWidth)
      //     .attr('height', _this.rowHeight-1 > 1? _this.rowHeight-1: _this.rowHeight)
      //     .attr('rx', _this.unitWidth / 5)
      //     .attr('fill', d => {
      //       return (d[stationId] === null || d[stationId] === 'null')?
      //           '#ffffff':
      //           _this.colorScale(_this.dataScale(d[stationId]))
      //     })
      //     .attr('stroke', 'white')
      //     .attr('stroke-width', 1);
      //
      // rects
      //     .append('title')
      //     .text(d=>{
      //       let _id = stationId in hkStationDict? hkStationDict[stationId]: stationId;
      //       let value = (d[stationId] === null || d[stationId] === 'null')? 'Null': parseInt(d[stationId] * 100) / 100;
      //       return 'Id: '+ _id + ' error: ' + value + '\nTimestamp: ' + format_date(new Date(d.timestamp * 1000));
      //     });

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
