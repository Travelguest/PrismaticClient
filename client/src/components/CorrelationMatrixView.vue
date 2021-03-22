<template>
  <div id='matrix' style='height: 100%'>
  </div>
</template>

<script>
import _ from 'lodash';
import * as d3 from 'd3';

export default {
  name: 'CorrelationMatrixView',
  components: {},
  props: {
    correlationMatrix: Object
  },
  emits: [
    'selectedStockFromMatrixDiagonal',
    'selectedStockFromMatrix'
  ],
  computed: {
    matrixColumn() {
      return !_.isEmpty(this.correlationMatrix)? this.correlationMatrix.columns: []
    },
    matrixCorr() {
      return !_.isEmpty(this.correlationMatrix)? this.correlationMatrix.corr: []
    },
  },
  data () {
    return {
      svg: null,
      width: 0,
      height: 0,
      margin: {top: 100, right: 40, bottom: 100, left: 0},
      padding: 0.05,
      legend: {yaxis: 40, xaxis: 20},

      colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,

    }
  },
  watch: {
    correlationMatrix: function() {
      this.renderMatrix();
    }
  },
  mounted() {
    console.log("correlationMatrix:",this.correlationMatrix);
    this.initMatrix();
    this.renderMatrix();
  },
  methods: {
    initMatrix() {
      // Initialize svg
      this.width = this.$el.clientWidth;
      this.height = this.$el.clientHeight;

      if (this.margin.left === 0 ){
        this.margin.left = this.width - (this.height - this.margin.top - this.margin.bottom);
      }
      this.svg = d3.select(this.$el).append('svg').attr('viewBox', [0, 0, this.width, this.height]);
    },
    renderMatrix() {
      // Remove all groups in svg
      this.svg.selectAll('g').remove();

      let heatmapContainer = this.svg
          .append('g')
          .attr('transform', `translate(${this.margin.left - this.margin.right},${this.margin.top})`)

      // Configuration
      let xAxis = g => g
          .call(d3.axisTop(x).tickSizeOuter(0));
      let yAxis = g => g
          .call(d3.axisLeft(y).tickSizeOuter(0));
      // .call(g => g.select('.domain').remove());
      let colorScale = d3.scaleSequential()
          .domain([-1,1])
          .interpolator(this.colorScheme);
      let x = d3.scaleBand()
          .domain(this.matrixColumn)
          .padding(this.padding)
          .range([0, this.width - this.margin.right - this.margin.left + this.legend.xaxis]);
      let y = d3.scaleBand()
          .domain(this.matrixColumn)
          .padding(this.padding)
          .range([0, this.height - this.margin.bottom - this.margin.top]);
      let r = (x(this.matrixColumn[1])-x(this.matrixColumn[0]))/2;

      // Heatmap
      heatmapContainer.append('g').call(xAxis);
      heatmapContainer.append('g').call(yAxis);
      heatmapContainer
          .selectAll('.cell')
          .data(this.matrixCorr)
          .enter()
          .append('rect')
          .attr('class', 'cell')
          .attr('x', d => x(d.col) )
          .attr('y', d => y(d.row) )
          .attr('width', x.bandwidth() )
          .attr('height', y.bandwidth() )
          .style('fill', d => colorScale(d.val) )
          .style('opacity', 1e-6)
          .transition()
          .style('opacity', 1);

      // Heatmap interaction
      d3.selectAll('.cell')
          .on('mouseover', function(_, d){
            d3.selectAll('.cell')
                .filter(k => !(k.col === d.col || k.row === d.row)) // when not in the same row or column
                .style('opacity', 0.3);
            d3.selectAll('.cell')
                .filter(k => (k.col === d.col || k.row === d.row) && (k.col !== k.row)) // when in the same row or column
                .style("stroke", "black")
                .style("stroke-width", 1);
          })
          .on('mouseout', function(){
            d3.selectAll('.cell')
                .style('opacity', 1)
                .filter(k => k.col !== k.row)
                .style("stroke-width", 0);
          });

      // The diagonal cells
      d3.selectAll('.cell')
          .filter(k => (k.col === k.row))
          // .style('fill', 'white')
          .attr("rx", r)
          .attr("ry", r)
          .style("fill", "white")
          .style("stroke", d => colorScale(d.val))
          .style("stroke-width", 4)
          .on('click', (_, d) => {
            this.$emit('selectedStockFromMatrixDiagonal', d.row);
          });

      d3.selectAll('.cell')
          .filter(k => (k.col !== k.row))
          .on('click', (_, d) => {
            this.$emit('selectedStockFromMatrix', d.row, d.col);
          });

      // legend scale
      let legendHeight = this.height - this.margin.top - this.margin.bottom,
          legend = this.svg.append('g')
              .attr('width', this.legend.xaxis)
              .attr('height', legendHeight)
              .attr('transform', `translate(${this.margin.left - this.margin.right*2 - this.legend.xaxis*2},${this.margin.top})`);

      let stops = d3.range(-1, 1.01, 0.2).map(d => {return {offset: (d+1)/2, color: colorScale(-d), value: -d}});
      legend.append('linearGradient')
          .attr('id', 'linear-gradient')
          .attr('x2', '0%')
          .attr('y2', '100%')
          .selectAll('stop')
          .data(stops)
          .enter().append('stop')
          .attr('offset', function(d){ return (100 * d.offset) + '%'; })
          .attr('stop-color', function(d){ return d.color; });
      legend.append('rect')
          .attr('width', this.legend.xaxis)
          .attr('height', legendHeight)
          .style('fill', 'url(#linear-gradient)');
      legend.selectAll('text')
          .data(stops)
          .enter().append('text')
          .attr('dx', -5)
          .attr('y', function(d){ return legendHeight * d.offset; })
          .style('text-anchor', 'end')
          .text(function(d){ return d.value.toFixed(1)});
    }
  }
}
</script>


<style scoped>
</style>